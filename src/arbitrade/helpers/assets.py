class Asset:
    def __init__(self, symbol, ib_symbol, kind, exchange, currency):
        self.symbol = symbol
        self.ib_symbol = ib_symbol
        self.local_symbol = None
        self.ib_local_symbol = None
        self.kind = kind
        self.exchange = exchange
        self.currency = currency
        self.price_series = None
    
    def set_price_series(self, df):
        self.price_series = df
    
    def set_local_symbol(self, local_symbol):
        self.local_symbol = local_symbol
    
    def set_ib_local_symbol(self, ib_local_symbol):
        self.ib_local_symbol = ib_local_symbol

    def get_price_series(self):
        return self.price_series
        
class Stock(Asset):
    pass

class Future(Asset):
    def __init__(self, symbol, ib_symbol, kind, exchange, currency, 
    mult, margin, include_months, exp_fmt, roll_days_before_exp):
        super().__init__(symbol, ib_symbol, kind, exchange, currency)
        self.mult = mult
        self.margin = margin
        self.include_months = include_months
        self.exp_fmt = exp_fmt
        self.roll_days_before_exp = roll_days_before_exp
        self.contfut_series = None
        self.expired_ib_local_symbol = None

    def set_contfut_series(self, df):
        self.contfut_series = df

    def set_expired_ib_local_symbol(self, expired_ib_local_symbol):
        self.expired_ib_local_symbol = expired_ib_local_symbol

    def get_expired_ib_local_symbol(self):
        return self.expired_ib_local_symbol

    def get_contfut_series(self):
        return self.contfut_series