from client import Client
from database import Database
from asset_controller import AssetController
from contract_controller import ContractController
from strategy_controller import StrategyController

if __name__ == "__main__":
    db = Database()
    db.connect()
    app = Client()
    app.connect()

    db.disconnect()
    app.disconnect()