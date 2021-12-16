import datetime as dt
import re
import configs

class HistoricalDataUpdate:
    def __init__(self, app, db, asset_builder, contract_builder):
        self.app = app
        self.db = db
        self.constants = configs.get_strategies()
        self.asset_builder = asset_builder
        self.contract_builder = contract_builder
        self.historical_data = []

    def __get_base_assets(self):
        bases = ()
        for strategy_details in self.constants["strategies"].values():            
            is_active = strategy_details["active"]
            if is_active:
                for item in strategy_details["assets"]:
                    if isinstance(item, list): # multi-leg spread
                        bases += tuple(self.asset_builder.build_base_asset(**leg) for leg in item)
                    else:
                        bases += (self.asset_builder.build_base_asset(**item),)
        return bases

    def __remove_duplicate_base_assets(self, bases):
        unique = ()
        for base in bases:
            if base.__dict__ not in [x.__dict__ for x in unique]:
                unique += (base,)
        return unique

    def __get_ib_contracts(self):
        bases = self.__remove_duplicate_base_assets(self.__get_base_assets())
        return {base.local_symbol: self.contract_builder.build_single_contract(base).make_ib_contract() for base in bases}

    def __get_historical_data(self, duration, bar_size):
        ib_contracts = self.__get_ib_contracts()
        all_bars = []
        for local_symbol, contract in ib_contracts.items():
            if contract.symbol == "VIX": continue # dont have mkt data for cfe right now
            bars = [[local_symbol] + bar for bar in self.app.request_historical_data(contract, duration, bar_size)]
            all_bars.extend(bars)
        return all_bars

    def update_historical_database(self, duration="3 D", bar_size="1 day"):
        bars = self.__get_historical_data(duration, bar_size)
        self.db.update_ts(bars)
        self.db.commit()

class AccountDataUpdate:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.constants = configs.get_constants()
    
    def __get_account_details(self):
        acc_details = self.app.request_account_details()
        acc_details["dt"] = dt.datetime.now(dt.timezone.utc)
        return acc_details
        
    def __regex_ib_local_symbol(self, symbol, ib_local_symbol):
        regex = self.constants["regex"].get(symbol, {}).get("ib_local_symbol")
        new = ib_local_symbol
        if regex:
            for args in regex:
                new = re.sub(*args, new)
            if re.search("MONTHCODE", new):
                verbose_month_code = re.search("(\s\s\s)(\w\w\w)(\s)", ib_local_symbol).group().strip()
                short_month_code = self.constants["month_codes"][verbose_month_code]
                new = re.sub("MONTHCODE", short_month_code, new)
        return new

    def __get_position_details(self):
        position_details = self.app.request_positions()
        utcnow = dt.datetime.now(dt.timezone.utc)
        rows = []
        for d in position_details:
            d["dt"] = utcnow
            d["LocalSymbol"] = self.__regex_ib_local_symbol(d["Symbol"], d["LocalSymbol"])
            rows.append([d["dt"], d["AccountCode"], d["LocalSymbol"], d["Position"], d["AvgCost"]])
        return rows

    def update_account_database(self):
        acc_details = self.__get_account_details()
        self.db.update_account(acc_details)
        self.db.commit()

    def update_position_database(self):
        rows = self.__get_position_details()
        self.db.update_positions(rows)
        self.db.commit()
    
    def __get_execution_details(self):
        exec_details = self.app.request_executions()
        rows = []
        for d in exec_details:
            d["LocalSymbol"] = self.__regex_ib_local_symbol(d["Symbol"], d["LocalSymbol"])
            rows.append([d["ExecTime"], d["AccountCode"], d["LocalSymbol"], d["TradeSize"], d["ExecPrice"]])
        return rows

    def update_transactions_database(self):
        rows = self.__get_execution_details()
        self.db.update_transactions(rows)
        self.db.commit()