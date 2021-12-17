from arbitrade.client.client import Client
from arbitrade.database.database import Database
from arbitrade.controllers.asset_builder import AssetBuilder
from arbitrade.controllers.contract_builder import ContractBuilder
from arbitrade.controllers.strategy_builder import StrategyBuilder
from arbitrade.controllers.execution import ExecutionController
from arbitrade.database.db_update import HistoricalDataUpdate, AccountDataUpdate
from arbitrade.controllers.cron_update import CronUpdate

class Controller:
    def __init__(self, tm, assets):
        self.app = Client()
        self.db = Database()
        self.tm = tm
        self.asset_builder = AssetBuilder(self.db)
        self.contract_builder = ContractBuilder(self.app)
        self.strategy_builder = StrategyBuilder(self.asset_builder, self.contract_builder, assets)

    def update_historical_database(self):
        hist_updates = HistoricalDataUpdate(self.app, self.db, self.strategy_builder)
        hist_updates.update_historical_database(self.tm)
    
    def execute(self):
        contract_forecast = self.strategy_builder.get_contract_forecast()
        execs = ExecutionController(self.app, contract_forecast)
        execs.execute()

    def update_account_database(self):
        acc_updates = AccountDataUpdate(self.app, self.db)
        acc_updates.update_account_database()
        acc_updates.update_position_database()
        acc_updates.update_transactions_database()
    
    def update_cronjobs(self):
        all_assets_builder = StrategyBuilder(self.asset_builder, self.contract_builder, "ALL")
        cron_updates = CronUpdate(self.app, all_assets_builder)
        cron_updates.update_cronjobs()
    
    def main(self):
        self.app.connect()
        self.app.reqGlobalCancel()
        self.db.connect()
        self.update_historical_database()
        self.execute()
        self.update_account_database()
        self.update_cronjobs()
        self.app.disconnect()
        self.db.disconnect()