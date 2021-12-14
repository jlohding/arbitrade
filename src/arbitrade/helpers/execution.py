import orders

class Execution:
    def __init__(self, app, positions, contract_forecast):
        self.app = app
        self.positions = positions
        self.forecast = contract_forecast

    def get_required_actions(self):
        actions = {}
        for contract, position in self.positions.items():
            actions[contract] = position * -1
        for contract, size in self.forecast:
            if contract in actions:
                actions[contract] += size
            else:
                actions[contract] = size
        return actions

    def execute(self):
        actions = self.get_required_orders()
        for contract, size in actions.items():
            self.app.place_order(contract, orders.create_market_order(size))