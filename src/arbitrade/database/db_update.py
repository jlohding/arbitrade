import datetime as dt
from arbitrade.conf.configs import AssetConstants

class HistoricalDataUpdate:
    def __init__(self, app, db, strategy_builder):
        self.app = app
        self.db = db
        self.strategy_builder = strategy_builder

    def __get_historical_data(self, tm, duration, bar_size):
        ib_contracts = self.strategy_builder.get_base_ib_contracts()
        all_bars = []
        for base, contract in ib_contracts.items():
            bars = [[base.local_symbol] + bar for bar in self.app.request_historical_data(contract, tm, duration, bar_size)]
            all_bars.extend(bars)
        return all_bars

    def update_historical_database(self, tm, duration="3 D", bar_size="1 day"):
        bars = self.__get_historical_data(tm, duration, bar_size)
        self.db.update_ts(bars)
        self.db.commit()

class AccountDataUpdate:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.constants = AssetConstants()
    
    def __get_account_details(self):
        acc_details = self.app.request_account_details()
        acc_details["dt"] = dt.datetime.now(dt.timezone.utc)
        return acc_details

    def __get_position_details(self):
        position_details = self.app.request_positions()
        utcnow = dt.datetime.now(dt.timezone.utc)
        rows = []
        for d in position_details:
            d["dt"] = utcnow
            d["LocalSymbol"] = self.constants.ib_local_symbol_to_local_symbol(d["Symbol"], d["LocalSymbol"])
            rows.append([d["dt"], d["AccountCode"], d["LocalSymbol"], d["Position"], d["AvgCost"]])
        return rows

    def __get_execution_details(self):
        exec_details = self.app.request_executions()
        rows = []
        for d in exec_details:
            d["LocalSymbol"] = self.constants.ib_local_symbol_to_local_symbol(d["Symbol"], d["LocalSymbol"])
            rows.append([d["ExecTime"], d["AccountCode"], d["LocalSymbol"], d["TradeSize"], d["ExecPrice"]])
        return rows

    def update_account_database(self):
        acc_details = self.__get_account_details()
        self.db.update_account(acc_details)
        self.db.commit()

    def update_position_database(self):
        rows = self.__get_position_details()
        self.db.update_positions(rows)
        self.db.commit()
    
    def update_transactions_database(self):
        rows = self.__get_execution_details()
        self.db.update_transactions(rows)
        self.db.commit()