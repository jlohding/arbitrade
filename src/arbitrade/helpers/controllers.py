import re
from client import Client
from database import Database
import assets
import contracts
import configs

class ContractController:
    def __init__(self, client):
        self.app = client
    
    def __get_conId(self, contract):
        contract_dets = self.app.get_contract_details(contract)
        conId = str(contract_dets.contract).split(",")[0]
        return conId

    def __get_composite_symbol(self, assets):
        '''
        Returns composite symbol for IB's contract.symbol

        From IB documentation: 
         - STK/STK combo | Alphabetical order, comma-separated: "AMD,BAC"
         - FUT/FUT same underlying | ib_symbol of the future
         - FUT/FUT inter-cmdty | local_symbol of inter-cmdty spread: "CL.BZ"
        '''
        if isinstance(assets[0], assets.Future) and isinstance(assets[1], assets.Future):
            if assets[0].ib_symbol == assets[1].ib_symbol:
                return assets[0].ib_symbol
            else:
                return assets[0].ib_symbol + "." + assets[1].ib_symbol
        elif isinstance(assets[0], assets.Stock) and isinstance(assets[1], assets.Stock):
            symbols = sorted([assets[0].ib_symbol, assets[1].ib_symbol])
            return ",".join(symbols)
        else:
            raise Exception("Invalid combo {[x.ib_symbol for x in assets]}")

    def construct_single_contract(self, asset, expired=False):
        args = {}
        if expired:
            args["localSymbol"] = asset.get_expired_local_symbol()
        else:
            args["localSymbol"] = asset.ib_local_symbol
        args["secType"] = asset.kind
        args["currency"] = asset.currency
        args["exchange"] = asset.exchange
        con = contracts.SingleContract(**args)
        con.set_conId(self.__get_conId(con.make_ib_contract()))
        return con

    def construct_composite_contract(self, assets, ratios, expired=False):
        args = {}
        args["contract_symbol"] = self.__get_composite_symbol(assets)
        args["secType"] = "BAG"
        args["currency"] = assets[0].currency
        args["exchange"] = assets[0].exchange
        composite = contracts.CompositeContract(**args)        
        for asset, size in zip(assets, ratios):
            con = self.construct_single_contract(asset, expired)
            composite.add_single_contract(con, size)
        return composite

class AssetController:
    def __init__(self, db):
        self.db = db
        self.constants = configs.get_constants()

    def format_ib_local_symbol(self, symbol, local_symbol):
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

    def construct_stock(self, ticker):
        args = self.__get_asset_constants(ticker, "STK")
        stk = assets.Stock(**args)
        stk.set_price_series(self.__get_price_series(ticker, "STK"))
        stk.set_local_symbol(self.__get_local_symbol(ticker, "STK"))
        stk.set_ib_local_symbol(self.format_ib_local_symbol(stk.symbol, stk.local_symbol))
        return stk

    def construct_future(self, ticker, contract_position, continuous_contract=False):
        if contract_position < 0:
            raise Exception("Contract position must be non-negative")
        args = self.__get_asset_constants(ticker, "FUT")
        fut = assets.Future(**args)
        if continuous_contract:
            fut.set_contfut_series(self.__get_contfut_series(ticker, contract_position, args["include_months"]))
        else:
            fut.set_price_series(self.__get_price_series(ticker, "FUT", contract_position, args["include_months"]))
        fut.set_contract_sequence(self.__get_contract_sequence(ticker, args["include_months"]))
        fut.set_local_symbol(self.__get_local_symbol(ticker, "FUT", contract_position, args["include_months"]))
        fut.set_ib_local_symbol(self.format_ib_local_symbol(fut.symbol, fut.local_symbol))
        return fut