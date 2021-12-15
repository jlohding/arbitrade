from ibapi.contract import Contract as ibContract
from ibapi.contract import ComboLeg as ibComboLeg

class Contract:
    def __init__(self, ib_symbol, localSymbol, secType, currency, exchange):
        self.assets = None
        self.contract_symbol = ib_symbol
        self.contract_local_symbol = localSymbol
        self.contract_kind = secType
        self.contract_currency = currency
        self.contract_exchange = exchange
        self.conId = 0

    def set_conId(self, conId):
        self.conId = conId

    def make_ib_contract(self):
        contract = ibContract()
        contract.symbol = self.contract_symbol
        contract.localSymbol = self.contract_local_symbol
        contract.secType = self.contract_kind
        contract.currency = self.contract_currency
        contract.exchange = self.contract_exchange
        contract.includeExpired = True
        if self.conId:
            contract.conId = self.conId
        return contract    

class SingleContract(Contract):
    def make_ib_comboleg(self, size):
        leg = ibComboLeg()
        leg.conId = self.conId
        leg.ratio = abs(size)
        leg.action = "BUY" if size > 0 else "SELL"
        leg.exchange = self.contract_exchange
        return leg

class CompositeContract(Contract):
    def __init__(self, ib_symbol, secType, currency, exchange):
        super().__init__(ib_symbol, None, secType, currency, exchange)
        self.single_contracts = []
        self.sizes = []

    def add_single_contract(self, c, size):
        self.single_contracts.append(c)
        self.sizes.append(size)
    
    def make_ib_contract(self):
        combolegs = [single_contract.make_ib_comboleg(size) for single_contract, size in zip(self.single_contracts, self.sizes)]
        contract = ibContract()
        contract.symbol = self.contract_symbol
        contract.secType = self.contract_kind
        contract.currency = self.contract_currency
        contract.exchange = self.contract_exchange
        contract.includeExpired = True
        contract.comboLegs = combolegs
        return contract