import pandas as pd

class Account:
    def __init__(self):
        self.pos_df = None
        self.orders = None
        self.exec = None
        self.acc_details = None
        self.contract_positions = {}
        self.historical_data = []
    
    def create_historical_data(self, bars):
        self.historical_data = []
        for bar in bars:
            dt, open_px, high_px, low_px, close_px, volume, open_int = [bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, 0]
            self.historical_data.append([dt, open_px, high_px, low_px, close_px, volume, open_int])
        return self.historical_data

    def create_contract_positions(self, data):
        self.contract_positions = {}
        for contract, position, *_ in data:
            if position != 0:
                contract.exchange = contract.primaryExchange if contract.secType == "FUT" else "SMART"
                self.contract_positions[contract] = position
        return self.contract_positions

    def create_positions_df(self, data):
        pos_list = []
        for account, contract, position, avgCost in data:
            pos_list.append((account, contract.symbol, contract.localSymbol,
                              contract.secType, contract.currency, position, avgCost))
            
        self.pos_df = pd.DataFrame(pos_list, 
                                   columns=['Account', 'Symbol', 'LocalSymbol', 
                                   'SecType', 'Currency', 'Position', 'Avg cost'])
        return self.pos_df

    def create_orders_df(self, data):
        order_list = []
        for orderId, contract, order, orderState in data:
            order_list.append((order.permId, order.clientId, orderId, 
                               order.account, contract.symbol, contract.secType,
                               contract.exchange, order.action, order.orderType,
                               order.totalQuantity, order.cashQty, order.lmtPrice, 
                               order.auxPrice, orderState.status))
        self.orders = pd.DataFrame(order_list, 
                                   columns=['PermId', 'ClientId', 'OrderId',
                                   'Account', 'Symbol', 'SecType',
                                   'Exchange', 'Action', 'OrderType',
                                   'TotalQty', 'CashQty', 'LmtPrice',
                                   'AuxPrice', 'Status'])
        return self.orders

    def create_account_details_dict(self, data):
        self.acc_details = data
    
    def create_executions_df(self, data):
        exec_list = []
        for contract, execution in data:
            exec_list.append((contract.symbol, contract.localSymbol, contract.secType, 
                              execution.time, execution.side, execution.shares, execution.price))
        self.exec = pd.DataFrame(exec_list, columns=['Symbol', 'LocalSymbol', 'SecType', 
                                            'Time', 'Side', 'Shares', 'Price'])
        self.exec.drop_duplicates(subset=["Symbol","LocalSymbol"], inplace=True)
        return self.exec