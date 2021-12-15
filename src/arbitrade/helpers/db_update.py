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
            print(local_symbol)
            if contract.symbol == "VIX": continue
            bars = [[local_symbol] + bar for bar in self.app.request_historical_data(contract, duration, bar_size)]
            all_bars.extend(bars)
        return all_bars

    def update_historical_database(self, duration="3 D", bar_size="1 day"):
        bars = self.__get_historical_data(duration, bar_size)
        
        self.db.update_ts(bars)
        self.db.commit()

