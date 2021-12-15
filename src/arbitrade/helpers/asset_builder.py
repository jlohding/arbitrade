import re
import configs
import assets

class AssetBuilder:
    def __init__(self, db):
        self.db = db
        self.constants = configs.get_constants()

    def __format_ib_local_symbol(self, symbol, local_symbol):
        regex = self.constants["regex"].get(symbol, {}).get("local_symbol")
        new = local_symbol
        if regex:
            for args in regex:
                new = re.sub(*args, new)
            if re.search("MONTHCODE", new):
                verbose_month_code = self.constants["month_codes"][local_symbol[2]]
                new = re.sub("MONTHCODE", verbose_month_code, new)
        return new

    def __get_asset_constants(self, ticker, kind):
        try:
            args = self.constants["assets"][kind][ticker]
        except KeyError:
            raise Exception(f"No {kind} with ticker {ticker} found in constants.yml")
        return args

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
        args = self.__get_asset_constants(ticker, kind)
        if kind == "STK":
            asset = assets.Stock(**args)
            asset.set_local_symbol(self.__get_local_symbol(ticker, "STK"))
            asset.set_ib_local_symbol(self.__format_ib_local_symbol(asset.symbol, asset.local_symbol))
        elif kind == "FUT":
            asset = assets.Future(**args)
            asset.set_local_symbol(self.__get_local_symbol(ticker, "FUT", contract_position, args["include_months"]))
            asset.set_ib_local_symbol(self.__format_ib_local_symbol(asset.symbol, asset.local_symbol))
        return asset

    def build(self, ticker, kind, contract_position=0, continuous_contract=False, **_):
        base = self.build_base_asset(ticker, kind, contract_position)
        if kind == "STK":
            return self.__build_stock(base)
        elif kind == "FUT":
            return self.__build_future(base, contract_position, continuous_contract)  