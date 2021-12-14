import assets
import contracts

class ContractController:
    def __init__(self, client):
        self.app = client
    
    def __get_conId(self, contract):
        contract_dets = self.app.get_contract_details(contract)
        conId = str(contract_dets.contract).split(",")[0]
        return int(conId)

    def __get_composite_symbol(self, asset_tup):
        '''
        Returns composite symbol for IB's contract.symbol

        From IB documentation: 
         - STK/STK combo | Alphabetical order, comma-separated: "AMD,BAC"
         - FUT/FUT same underlying | ib_symbol of the future
         - FUT/FUT inter-cmdty | local_symbol of inter-cmdty spread: "CL.BZ"
        '''
        if isinstance(asset_tup[0], assets.Future) and isinstance(asset_tup[1], assets.Future):
            if asset_tup[0].ib_symbol == asset_tup[1].ib_symbol:
                return asset_tup[0].ib_symbol
            else:
                return asset_tup[0].ib_symbol + "." + asset_tup[1].ib_symbol
        elif isinstance(asset_tup[0], assets.Stock) and isinstance(asset_tup[1], assets.Stock):
            symbols = sorted([asset_tup[0].ib_symbol, asset_tup[1].ib_symbol])
            return ",".join(symbols)
        else:
            raise Exception("Invalid combo {[x.ib_symbol for x in assets]}")

    def construct_single_contract(self, asset, expired=False):
        args = {}
        if expired:
            args["localSymbol"] = asset.get_expired_ib_local_symbol()
        else:
            args["localSymbol"] = asset.ib_local_symbol
        args["secType"] = asset.kind
        args["currency"] = asset.currency
        args["exchange"] = asset.exchange
        con = contracts.SingleContract(**args)
        con.set_conId(self.__get_conId(con.make_ib_contract()))
        return con

    def construct_composite_contract(self, asset_tup, ratio_tup, expired=False):
        args = {}
        args["contract_symbol"] = self.__get_composite_symbol(asset_tup)
        args["secType"] = "BAG"
        args["currency"] = asset_tup[0].currency
        args["exchange"] = asset_tup[0].exchange
        composite = contracts.CompositeContract(**args)        
        for asset, size in zip(asset_tup, ratio_tup):
            con = self.construct_single_contract(asset, expired)
            composite.add_single_contract(con, size)
        return composite