import orders

class ExecutionController:
    def __init__(self, app, contract_forecast):
        self.app = app
        self.contract_positions = self.app.request_contract_positions()
        self.forecast = contract_forecast

    def get_required_actions(self):
        actions = {}
        for contract, position in self.contract_positions.items():
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
                #contract.conId = 0
                print(contract.__dict__)
                order = create_market_order(size)
                self.app.place_order(contract, order)