import os
from copy import deepcopy
from configparser import ConfigParser, ExtendedInterpolation
import re
import yaml

def get_config(section, fname="config.ini"):
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    parser.optionxform=str
    path = os.path.dirname(os.path.realpath(__file__))    
    parser.read(os.path.join(path, fname))

    if parser.has_section(section):
        params = parser.items(section)
        args = {p[0]: p[1] for p in params}
    else:
        raise Exception(f"{section} not found in {fname}")
    return args

def get_queries():
    get_config("paths")["sql"]
    with open(get_config("paths")["sql"], "r") as stream:
        return yaml.safe_load(stream)

class AssetConstants:
    def __init__(self):
        with open(get_config("paths")["assets"], "r") as stream:
            self.constants = yaml.safe_load(stream)
    
    def get_asset_constants(self, ticker, kind):
        try:
            args = self.constants["assets"][kind][ticker]
        except KeyError:
            raise Exception(f"No {kind} with ticker {ticker} found in constants.yml")
        return args

    def local_symbol_to_ib_local_symbol(self, symbol, local_symbol):
        regex = self.constants["regex"].get(symbol, {}).get("ib_local_symbol")
        new = local_symbol
        if regex:
            for args in regex:
                new = re.sub(*args, new)
            if re.search("MONTHCODE", new):
                verbose_month_code = self.constants["month_codes"][local_symbol[2]]
                new = re.sub("MONTHCODE", verbose_month_code, new)
        return new

    def ib_local_symbol_to_local_symbol(self, symbol, ib_local_symbol):
        regex = self.constants["regex"].get(symbol, {}).get("local_symbol")
        new = ib_local_symbol
        if regex:
            for args in regex:
                new = re.sub(*args, new)
            if re.search("MONTHCODE", new):
                verbose_month_code = re.search("(\s\s\s)(\w\w\w)(\s)", ib_local_symbol).group().strip()
                short_month_code = self.constants["month_codes"][verbose_month_code]
                new = re.sub("MONTHCODE", short_month_code, new)
        return new

    def ib_symbol_to_symbol(self, ib_symbol):
        regex = self.constants["regex"].get(ib_symbol, {}).get("symbol")
        new = ib_symbol
        if regex:
            for args in regex:
                new = re.sub(*args, new)
        return new

class StrategyConstants:
    def __init__(self, asset_filter):
        with open(get_config("paths")["strategies"], "r") as stream:
            self.constants = yaml.safe_load(stream)
        self.__filter_assets(asset_filter) 
    
    def __filter_assets(self, asset_filter):
        if asset_filter == "ALL":
            return
        strats = deepcopy(self.constants["strategies"])
        for strat_idx, strat in strats.items():
            for item in strat["assets"]:
                if isinstance(item, list):
                    for leg in item:
                        if (leg["ticker"], leg["kind"]) not in asset_filter:
                            self.constants["strategies"][strat_idx]["assets"].remove(item)
                            break
                else:
                    if (leg["ticker"], leg["kind"]) not in asset_filter:
                        self.constants["strategies"][strat_idx]["assets"].remove(item)
                            
    def get_strategies(self):
        return self.constants["strategies"].values()