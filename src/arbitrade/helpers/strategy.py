import signals

class Strategy:
    def __init__(self, name, portfolio_weight, assets):
        self.name = name
        self.portfolio_weight = portfolio_weight
        self.assets = assets
    
    def __forecast(self, asset):
        return signals.get_forecast(self.name, asset)

    def get_forecasts(self):
        forecast = {}
        for asset in self.assets:
            forecast[asset] = self.__forecast(asset)
        return forecast