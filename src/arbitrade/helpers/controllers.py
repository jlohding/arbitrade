from client import Client
from database import Database
from asset_controller import AssetController
from contract_controller import ContractController
from strategy_controller import StrategyController
from execution import Execution

def main():
    db = Database()
    app = Client()    
    db.connect()
    app.connect()

    strat_control = StrategyController(AssetController(db), ContractController(app))
    contract_forecast = strat_control.get_contract_forecast()
    execs = Execution(app, contract_forecast)
    execs.execute()

    app.disconnect()
    db.disconnect()

if __name__ == "__main__":
    main()