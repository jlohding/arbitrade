from arbitrade.controllers.models import orders

class ExecutionController:
    def __init__(self, app, contract_forecast):
        self.app = app
        self.contract_positions = self.app.request_contract_positions()
        self.forecast = contract_forecast

    def get_required_actions(self):
        actions = {}
        for contract, position in self.contract_positions.items():
            if (contract.symbol, contract.secType) in [(c.symbol, c.secType) for c in self.forecast]:
                actions[contract] = position * -1
        for contract, size in self.forecast.items():
            for existing_contract in actions:
                if existing_contract.conId == contract.conId: # merge identical conIds
                    actions[existing_contract] += size
                    break
            else: 
                actions[contract] = size
        return actions

    def execute(self):
        actions = self.get_required_actions()
        create_market_order = orders.market_order_factory()
        for contract, size in actions.items():
            if size != 0:
                order = create_market_order(size)
                self.app.place_order(contract, order)