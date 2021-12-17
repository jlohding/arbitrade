import datetime as dt
import zoneinfo
import arbitrade.conf.configs as configs

class CronUpdate:
    def __init__(self, app, strategy_builder):
        self.app = app
        self.strategy_builder = strategy_builder
        self.constants = configs.AssetConstants()

    def __get_contract_details(self):
        ib_contracts = self.strategy_builder.get_base_ib_contracts()
        contract_details = [(self.constants.ib_symbol_to_symbol(contract.symbol), 
                             contract.secType, 
                             self.app.get_contract_details(contract)) 
                             for contract in ib_contracts.values()]
        return contract_details
    
    def __get_tz_offset(self, timezone):
        delta = dt.datetime.now(zoneinfo.ZoneInfo(timezone)).utcoffset()
        return delta

    def __parse_utc_hours(self, trading_hours, tz_offset):
        open_hours = []
        sessions = trading_hours.split(";")
        for session in sessions:
            if "CLOSED" in session:
                continue
            else:
                start, end = session.split("-")
                utc_start, utc_end = [dt.datetime.strptime(tm, "%Y%m%d:%H%M") - tz_offset for tm in (start, end)]
                aware_utc_start, aware_utc_end = [t.replace(tzinfo=zoneinfo.ZoneInfo("UTC")) for t in (utc_start, utc_end)]
                open_hours.append((aware_utc_start, aware_utc_end))
        return open_hours

    def __get_contract_open_hours(self):
        contract_details = self.__get_contract_details()
        utc_open_hours_d = {(symbol, kind): (self.__parse_utc_hours(det.tradingHours, self.__get_tz_offset(det.timeZoneId))) for symbol, kind, det in contract_details}
        return utc_open_hours_d

    def __get_next_session_open(self):
        utc_open_hours_d = self.__get_contract_open_hours()
        utcnow = dt.datetime.now(zoneinfo.ZoneInfo("UTC"))
        next_session_d = {}

        for asset, sessions in utc_open_hours_d.items():
            for start, end in sessions:
                if utcnow < start:
                    next_session_d[asset] = start
                    break
            else:
                raise Exception(f"No next open found for {asset}")
        return next_session_d
    
    def __get_cron_d(self):
        next_session_d = self.__get_next_session_open()
        cron_d = {}
        for asset, dt in next_session_d.items():
            cron = f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
            dt_string = dt.strftime("%Y%m%d %H:%M:%S")
            if (cron, dt_string) not in cron_d:
                cron_d[(cron, dt_string)] = []
            cron_d[(cron, dt_string)].append(asset)
        return cron_d
    
    def update_cronjobs(self):
        cron_d = self.__get_cron_d()
        commands = []
        for key, assets in cron_d.items():
            cron, dt_string = key
            asset_string = " ".join([",".join(asset) for asset in assets])
            
            command = configs.get_config("commands")["cron"].format(cron, asset_string, dt_string)
            commands.append(command)
        
        with open(configs.get_config("paths")["cron"], "w") as file:
            for command in commands:
                file.write(command+"\n")