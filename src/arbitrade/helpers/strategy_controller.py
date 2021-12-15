import configs
import strategy

class StrategyController:
    def __init__(self, asset_controller, contract_controller):
        self.asset_controller = asset_controller
        self.contract_controller = contract_controller
        self.constants = configs.get_strategies()

    def __construct_strategies(self):
        strategies = []
        for strategy_details in self.constants["strategies"].values():
            args = {} 
            is_active = strategy_details["active"]
            if is_active:
                assets = ()
                for item in strategy_details["assets"]:
                    if isinstance(item, list): # multi-leg spread
                        bag = tuple((self.asset_controller.construct_asset(**leg), leg["ratio"]) for leg in item)
                        assets += (bag,)
                    else:
                        asset = self.asset_controller.construct_asset(**item)
                        assets += (asset,)
                args["name"] = strategy_details["name"]
                args["portfolio_weight"] = strategy_details["portfolio_weight"]
                args["assets"] = assets
                strategies.append(self.__construct_strategy(args))
        return strategies

    def __construct_strategy(self, args):
        return strategy.Strategy(**args)

    def get_contract_forecast(self):
        forecast = self.get_asset_forecast()
        new_forecast = {}
        for asset, size in forecast.items():
            contract = self.contract_controller.construct_single_contract(asset)
            new_forecast[contract.make_ib_contract()] = size
        return new_forecast

    def get_asset_forecast(self):
        strategies = self.__construct_strategies()
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