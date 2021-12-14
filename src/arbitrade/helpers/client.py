import threading
import datetime as dt
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.execution import ExecutionFilter
from configs import get_config
from histdata import HistData
from account import Account

class Client(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.hist_data = HistData()
        self.account = Account()

    def log(self, message):
        tm = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d %H:%M:%S %Z")
        print(f"{tm} | {message}")

    def connect(self):
        self.connection_flag = threading.Event()
        args = get_config("ibapi")
        self.account_code = args["accountCode"]
        super().connect(args["host"], int(args["port"]), int(args["clientId"]))
        connection_thread = threading.Thread(target=lambda: self.run(), daemon=True)
        connection_thread.start() 
        self.connection_flag.wait()
        self.log("Websocket connection OPEN")

    def nextValidId(self, orderId): #callback on self.connect()
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        self.log(f"NextValidOrderId: {self.nextValidOrderId}")
        self.connection_flag.set()
    
    def connectionClosed(self): # callback on self.disconnect()
        self.log("Websocket connection CLOSED")

    # historical data
    def request_historical_data(self, contract, duration="5 D", bar_size="1 day"):
        self.req_histdata_flag = threading.Event()
        self.bars = []
        utcnow = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d %H:%M:%S")
        self.reqHistoricalData(reqId=app.nextValidOrderId,
                               contract=contract,
                               endDateTime=utcnow,
                               durationStr=duration,
                               barSizeSetting=bar_size,
                               whatToShow="TRADES",
                               useRTH=0,
                               formatDate=1,
                               keepUpToDate=0,
                               chartOptions=[])
        self.req_histdata_flag.wait()
        self.hist_data.create_bars(contract, self.bars)

    def historicalData(self, reqId, bar): 
        self.bars.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.req_histdata_flag.set()

    # execution
    def place_order(self, contract, order):
        self.order_exec_flag = threading.Event()            
        self.placeOrder(self.nextValidOrderId,
                         contract,
                         order)
        self.order_exec_flag.wait()

    def __comboleg_executed(self, execId):
        return True if execId.endswith("03.01") else False

    def execDetails(self, reqId, contract, execution):
        try:
            self.exec_details.append((contract, execution))
        except AttributeError:
            pass
        
        try:
            if contract.secType == "BAG": # not sure if this will work
                if self.__comboleg_executed(execution.execId):
                    self.order_exec_flag.set()
            else:
                self.order_exec_flag.set()
        except AttributeError:
            pass


    def request_executions(self):
        self.req_exec_flag = threading.Event()
        self.exec_details = []
        self.reqExecutions(self.nextValidOrderId, ExecutionFilter())
        self.req_exec_flag.wait()
        self.account.create_executions_df(self.exec_details)

    def execDetailsEnd(self, reqId):
        self.req_exec_flag.set()

    # positions
    def request_positions(self):
        self.req_positions_flag = threading.Event()
        self.pos_list = []
        self.reqPositions()
        self.req_positions_flag.wait()
        self.account.create_positions_df(self.pos_list)

    def position(self, account, contract, position, avgCost):
        self.pos_list.append((account, contract, position, avgCost))
    
    def positionEnd(self):
        self.cancelPositions()
        self.req_positions_flag.set()

    # orders
    def request_open_orders(self):
        self.open_order_flag = threading.Event()
        self.orders_list = []
        self.reqAllOpenOrders()
        self.open_order_flag.wait()
        self.account.create_orders_df(self.orders_list)
        return self.orders_list

    def openOrder(self, orderId, contract, order, orderState):
        self.orders_list.append((orderId, orderId, contract, order, orderState))

    def openOrderEnd(self):
        self.open_order_flag.set()

    # account details
    def __request_daily_pnl(self):
        self.pnl_flag = threading.Event()
        self.daily_pnl = 0
        self.reqPnL(self.nextValidOrderId, self.account_code, "")
        self.pnl_flag.wait()
        return self.daily_pnl

    def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
        self.daily_pnl  = dailyPnL
        self.cancelPnL(self.nextValidOrderId)
        self.pnl_flag.set()

    def request_account_details(self):
        self.acc_details_flag = threading.Event()
        self.acc_details = {}
        self.reqAccountSummary(self.nextValidOrderId, 
                               "All", "$LEDGER:ALL")
        self.acc_details_flag.wait()
        self.acc_details["DailyPnL"] = self.__request_daily_pnl()
        self.account.create_account_details_dict(self.acc_details)
    
    def accountSummary(self, reqId, account, tag, value, currency):
        self.acc_details[tag] = value

    def accountSummaryEnd(self, reqId):
        self.cancelAccountSummary(self.nextValidOrderId)
        self.acc_details_flag.set()

    def request_account_updates(self):
        self.acc_update_flag = threading.Event()
        self.acc_updates = []
        self.reqAccountUpdates(True, self.account_code)
        self.acc_update_flag.wait()
        return self.acc_updates
    
    def updatePortfolio(self, *details):
        self.acc_updates.append(details)

    def accountDownloadEnd(self, accountName):
        self.acc_update_flag.set()

    # contract details
    def get_contract_details(self, contract):
        self.contract_det_flag = threading.Event()
        self.contract_dets = None
        self.reqContractDetails(self.nextValidOrderId, contract)
        self.contract_det_flag.wait()
        return self.contract_dets

    def contractDetails(self, reqId, contractDetails):
        self.contract_dets = contractDetails

    def contractDetailsEnd(self, reqId):
         self.contract_det_flag.set()