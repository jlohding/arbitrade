import configs
import strategy

class StrategyController:
    def __init__(self, asset_controller):
        self.asset_controller = asset_controller
        self.constants = configs.get_strategies()
    
    #self.asset_controller.construct_future(ticker, contract_position, continuous_contract=False):
    def construct_strategies(self):
        d = self.constants["strategies"]
        strats = []
        for strategy_dict in d.values():
            name = strategy_dict.get("name")
            portfolio_weight = strategy_dict.get("portfolio_weight")
            asset_dict = strategy_dict.get("assets")

            all_assets = []
            for asset_type, values in asset_dict.items():
                if asset_type == "FUT":
                    for ticker, contract_position in values:
                        asset = self.asset_controller.construct_asset(ticker, "FUT", contract_position, True)
                        all_assets.append(asset)
                elif asset_type == "STK":
                    for ticker in values:
                        asset = self.asset_controller.construct_asser(ticker, "STK")
                elif asset_type == "BAG":
                    for bag in values:
                        spread = []
                        for *args, size in bag:
                            asset = self.asset_controller.construct_asset(*args)
                            spread.append([asset, size])
                        all_assets.append(spread)

            strat = strategy.Strategy(name, portfolio_weight, all_assets)
            strats.append(strat)
        return strats

    def construct_strategy(self):
        args = ""
        strat = strategy.Strategy(**args)
        return strat

    def convert_forecast_to_order(self):
        # maybe not here?
        pass