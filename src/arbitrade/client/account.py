class Account:    
    def create_historical_data(self, bars):
        historical_data = []
        for bar in bars:
            dt, open_px, high_px, low_px, close_px, volume, open_int = [bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, 0]
            historical_data.append([dt, open_px, high_px, low_px, close_px, volume, open_int])
        return historical_data

    def create_contract_positions(self, data):
        contract_positions = {}
        for contract, position, *_ in data:
            if position != 0:
                contract.exchange = contract.primaryExchange if contract.secType == "FUT" else "SMART" # need fix
                contract_positions[contract] = position
        return contract_positions

    def create_position_details(self, data):
        pos_details = []
        for account, contract, position, avgCost in data:
            d = {"AccountCode": account, "Symbol": contract.symbol, "LocalSymbol": contract.localSymbol, 
                "Position": position, "AvgCost": avgCost}
            pos_details.append(d)
        return pos_details

    def create_account_details_dict(self, account_code, data):
        target_keys = ("TotalCashBalance", "RealizedPnL", "UnrealizedPnL", "MaintMarginReq")
        acc_details = {k: round(float(data.get(k, 0)),5) for k in target_keys}
        acc_details["AccountCode"] = account_code
        return acc_details

    def create_execution_details(self, data):
        exec_details = []
        for contract, execution in data:
            trade_size = execution.shares if execution.side == "BOT" else execution.shares * -1
            d = {"ExecTime": execution.time, "AccountCode": execution.acctNumber, "Symbol": contract.symbol, 
                 "LocalSymbol": contract.localSymbol, "TradeSize": trade_size, "ExecPrice": execution.price}
            exec_details.append(d)
        return exec_details