import datetime as dt
import pandas as pd
import psycopg2
from configs import get_config
from configs import get_queries

class Database:
    def __init__(self):
        self.commits = 0
        self.queries = get_queries()

    def log(self, message, timestamp=True):
        tm = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d %H:%M:%S %Z")
        if timestamp:
            print(f"{tm} | {message}")
        else:
            print(message)

    def connect(self):
        args = get_config("postgresql")
        self.log("Connecting to PostgreSQL DB...")
        try:
            self.conn = psycopg2.connect(**args)
            self.cur = self.conn.cursor()

            self.cur.execute("SELECT version()")
            self.log(self.cur.fetchone()[0])
            self.cur.close()
        except psycopg2.DatabaseError as e:
            self.log(e)

    def disconnect(self):
        self.conn.close()
        self.log("DB connection closed.")

    def commit(self):
        self.conn.commit()
        self.log(f"Affected {self.commits} rows.")
        self.commits = 0

    def execute(self, sql, args=(), multi=False):
        self.cur = self.conn.cursor()
        if multi:
            self.cur.executemany(sql, args)
        else:
            self.cur.execute(sql, args)
        self.commits += self.cur.rowcount

    def read_table(self, table_name, mute=False):
        df = pd.read_sql(f"SELECT * FROM {table_name}", self.conn)
        if not mute:
            self.log(df, timestamp=False)
        return df

    def update_active_contracts(self):
        sql = self.queries['update_active_contracts']
        self.execute(sql)

    def get_underlying_id(self, symbol, kind):
        sql = self.queries['get_underlying_id']
        self.execute(sql, (symbol, kind))
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            raise Exception(f"({symbol},{kind}) not found in table underlying")

    def get_contract_sequence(self, symbol, kind, include_months=()):  
        underlying_id = self.get_underlying_id(symbol, kind)
        sql = self.queries['get_contract_sequence'][kind]

        if include_months:
            filter_months = [symbol+month+"__" for month in include_months]
            self.execute(sql, (underlying_id, filter_months))
        else:
            self.execute(sql, (underlying_id,))

        contracts = self.cur.fetchall()
        return contracts
    # ------------
    def insert_underlying(self, *data):
        sql = "INSERT INTO underlying VALUES(DEFAULT,%s,%s,%s) ON CONFLICT (symbol, kind) DO NOTHING"        
        self.execute(sql, data)

        return self.read_table("underlying")

    def insert_contract(self, symbol, kind, *data):
        sql = "INSERT INTO contract VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (local_symbol) DO NOTHING"
        underlying_id = self.get_underlying_id(symbol, kind)
        self.execute(sql, (underlying_id,)+data)

        return self.read_table("contract")

    def insert_ts(self, local_symbol, data):
        sql = '''INSERT INTO time_series VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (local_symbol, dt) DO NOTHING'''
        self.execute(sql, data)

        return self.read_table("time_series")
    # -------------
    def get_price_series(self, symbol, kind, contract_position, include_months=()): # get unadjusted time series 
        contracts = self.get_contract_sequence(symbol, kind, include_months)
        sql = self.queries['get_price_series']
        self.execute(sql[0])
        
        start = dt.date.min
        for idx, contract in enumerate(contracts):
            if idx+contract_position >= len(contracts): # catch IndexError
                break
            else:
                local_symbol, expiry = contract
                offset_local_symbol = contracts[idx+contract_position][0]
                self.execute(sql[1], (offset_local_symbol, start, expiry))
                start = expiry
                             
        df = self.read_table("temp_df", mute=True)
        self.execute("DELETE FROM temp_df")
        return df

    def get_contfut_df(self, symbol, contract_position, include_months):
        '''
        Panama Stitched Continuous Contract
        '''
        raw_df = self.get_price_series(symbol, "FUT", contract_position, include_months)
        df = raw_df.copy()
        filter_roll_days = df[df["local_symbol"].ne(df["local_symbol"].shift())]        
        filter_roll_days["prev_contract"] = filter_roll_days.local_symbol.shift(1)
        for row in filter_roll_days.iloc[1:].itertuples():
            sql = self.queries['get_contfut_df']
            self.execute(sql, (row.prev_contract, row.dt))
            expiry_price = self.cur.fetchone()
            if expiry_price:
                gap = row.close_px - float(expiry_price[0]) 
                raw_df.loc[raw_df.index[:row.Index], ["open_px","high_px","low_px","close_px"]] += gap 
        return raw_df

    def get_active_local_symbol(self, symbol, kind, contract_position=0, include_months=()):
        self.update_active_contracts()
        underlying_id = self.get_underlying_id(symbol, kind)
        sql = self.queries['get_active_local_symbol'][kind]
        if include_months:
            filter_months = [symbol+month+"__" for month in include_months]
            self.execute(sql, (underlying_id, filter_months))
        else:
            self.execute(sql, (underlying_id,))
        return self.cur.fetchall()[contract_position][0]
