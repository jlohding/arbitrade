from configs import StrategyConstants
import strategy

class StrategyBuilder:
    def __init__(self, asset_builder, contract_builder, asset_filter):
        self.asset_builder = asset_builder
        self.contract_builder = contract_builder
        self.constants = StrategyConstants(asset_filter)

    def __build_base_assets(self):
        bases = ()
        for strategy_details in self.constants.get_strategies():            
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

    def __build_strategies(self):
        strategies = []
        for strategy_details in self.constants.get_strategies():
            args = {} 
            is_active = strategy_details["active"]
            if is_active:
                assets = ()
                for item in strategy_details["assets"]:
                    if isinstance(item, list): # multi-leg spread
                        bag = tuple((self.asset_builder.build(**leg), leg["ratio"]) for leg in item)
                        assets += (bag,)
                    else:
                        asset = self.asset_builder.build(**item)
                        assets += (asset,)
                args["name"] = strategy_details["name"]
                args["portfolio_weight"] = strategy_details["portfolio_weight"]
                args["assets"] = assets
                strategies.append(self.__build_strategy(args))
        return strategies

    def __build_strategy(self, args):
        return strategy.Strategy(**args)

    def __get_asset_forecast(self):
        strategies = self.__build_strategies()
        forecast = {}
        for strat in strategies:
            d = strat.get_forecasts()
            for asset, size in d.items():
                if isinstance(asset, tuple): # spread
                    for a, ratio in asset:
                        if a not in forecast:
                            forecast[a] = ratio*size 
                        else:
                            forecast[a] += ratio*size
                else:
                    if asset not in forecast:
                        forecast[asset] = size
                    else:
                        forecast[asset] += size
        return forecast

    def get_contract_forecast(self):
        forecast = self.__get_asset_forecast()
        new_forecast = {}
        for asset, size in forecast.items():
            contract = self.contract_builder.build_single_contract(asset)
            new_forecast[contract.make_ib_contract()] = size
        return new_forecast
    
    def get_base_ib_contracts(self):
        bases = self.__remove_duplicate_base_assets(self.__build_base_assets())
        return {base: self.contract_builder.build_single_contract(base).make_ib_contract() for base in bases}