from arbitrade.conf.configs import AssetConstants
from arbitrade.controllers.models import assets

class AssetBuilder:
    def __init__(self, db):
        self.db = db
        self.constants = AssetConstants()

    def __get_local_symbol(self, ticker, kind, contract_position=0, include_months=()):
        return self.db.get_active_local_symbol(ticker, kind, contract_position, include_months)

    def __get_price_series(self, ticker, kind, contract_position=0, include_months=()):
        return self.db.get_price_series(ticker, kind, contract_position, include_months)

    def __get_contfut_series(self, ticker, contract_position, include_months):
        return self.db.get_contfut_df(ticker, contract_position, include_months)

    def __build_stock(self, base):
        base.set_price_series(self.__get_price_series(base.symbol, "STK"))
        return base

    def __build_future(self, base, contract_position, continuous_contract=False):
        if contract_position < 0:
            raise Exception("Contract position must be non-negative")

        if continuous_contract:
            base.set_price_series(self.__get_contfut_series(base.symbol, contract_position, base.include_months))
        else:
            base.set_price_series(self.__get_price_series(base.symbol, "FUT", contract_position, base.include_months))
        return base

    def build_base_asset(self, ticker, kind, contract_position, **_):
        args = self.constants.get_asset_constants(ticker, kind)
        if kind == "STK":
            asset = assets.Stock(**args)
            asset.set_local_symbol(self.__get_local_symbol(ticker, "STK"))
            asset.set_ib_local_symbol(self.constants.local_symbol_to_ib_local_symbol(asset.symbol, asset.local_symbol))
        elif kind == "FUT":
            asset = assets.Future(**args)
            asset.set_local_symbol(self.__get_local_symbol(ticker, "FUT", contract_position, args["include_months"]))
            asset.set_ib_local_symbol(self.constants.local_symbol_to_ib_local_symbol(asset.symbol, asset.local_symbol))
        return asset

    def build(self, ticker, kind, contract_position=0, continuous_contract=False, **_):
        base = self.build_base_asset(ticker, kind, contract_position)
        if kind == "STK":
            return self.__build_stock(base)
        elif kind == "FUT":
            return self.__build_future(base, contract_position, continuous_contract)  