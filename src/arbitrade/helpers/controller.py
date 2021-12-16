from client import Client
from database import Database
from asset_builder import AssetBuilder
from contract_builder import ContractBuilder
from strategy_builder import StrategyBuilder
from execution import ExecutionController
from db_update import HistoricalDataUpdate
from db_update import AccountDataUpdate

def main():
    db = Database()
    app = Client()    
    db.connect()
    app.connect()

    #app.reqGlobalCancel()
    asset_builder = AssetBuilder(db)
    contract_builder = ContractBuilder(app)
    
    #'''
    updates = HistoricalDataUpdate(app, db, asset_builder, contract_builder)
    updates.update_historical_database()
    #'''

    #'''
    strategy_builder = StrategyBuilder(asset_builder, contract_builder)
    contract_forecast = strategy_builder.get_contract_forecast()
    execs = ExecutionController(app, contract_forecast)
    execs.execute()
    #'''

    #'''
    acc_updates = AccountDataUpdate(app, db)
    acc_updates.update_account_database()
    acc_updates.update_position_database()
    acc_updates.update_transactions_database()
    #'''
    
    app.disconnect()
    db.disconnect()

if __name__ == "__main__":
    main()