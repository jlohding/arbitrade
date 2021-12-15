import re
import configs
import assets

class AssetBuilder:
    def __init__(self, db):
        self.db = db
        self.constants = configs.get_constants()

    def __format_ib_local_symbol(self, symbol, local_symbol):
        regex = self.constants["regex"].get(symbol, {}).get("local_symbol")
        verbose_month_code = self.constants["month_codes"][local_symbol[2]]
        if regex:
            for args in regex:
                local_symbol = re.sub(*args, local_symbol)
            if re.search("MONTHCODE", local_symbol):
                local_symbol = re.sub("MONTHCODE", verbose_month_code, local_symbol)
        return local_symbol

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

    def __get_contract_sequence(self, ticker, include_months):
        return [x[0] for x in self.db.get_contract_sequence(ticker, "FUT", include_months)]

    def __get_expired_local_symbol(self, local_symbol, contract_sequence):
        idx = contract_sequence.index(local_symbol)
        return contract_sequence[idx-1]

    def __build_stock(self, ticker):
        args = self.__get_asset_constants(ticker, "STK")
        stk = assets.Stock(**args)
        stk.set_price_series(self.__get_price_series(ticker, "STK"))
        stk.set_local_symbol(self.__get_local_symbol(ticker, "STK"))
        stk.set_ib_local_symbol(self.__format_ib_local_symbol(stk.symbol, stk.local_symbol))
        return stk

    def __build_future(self, ticker, contract_position, continuous_contract=False):
        if contract_position < 0:
            raise Exception("Contract position must be non-negative")
        args = self.__get_asset_constants(ticker, "FUT")
        fut = assets.Future(**args)
        if continuous_contract:
            fut.set_contfut_series(self.__get_contfut_series(ticker, contract_position, args["include_months"]))
        else:
            fut.set_price_series(self.__get_price_series(ticker, "FUT", contract_position, args["include_months"]))

        fut.set_local_symbol(self.__get_local_symbol(ticker, "FUT", contract_position, args["include_months"]))
        fut.set_ib_local_symbol(self.__format_ib_local_symbol(fut.symbol, fut.local_symbol))
        exp_local_symbol = self.__get_expired_local_symbol(fut.local_symbol, self.__get_contract_sequence(ticker, args["include_months"])) 
        fut.set_expired_ib_local_symbol(self.__format_ib_local_symbol(ticker, exp_local_symbol))
        return fut

    def build(self, ticker, kind, contract_position=0, continuous_contract=False, **_):
        if kind == "STK":
            return self.__build_stock(ticker)
        elif kind == "FUT":
            return self.__build_future(ticker, contract_position, continuous_contract)  