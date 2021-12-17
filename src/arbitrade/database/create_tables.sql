CREATE TABLE underlying (
    underlying_id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    kind VARCHAR(3),
    currency VARCHAR(3),
    active_contract VARCHAR(10) DEFAULT NULL, -- this is the local_symbol of the current active contract
    UNIQUE(symbol, kind)
);

CREATE TABLE contract (
    underlying_id SERIAL,
    local_symbol VARCHAR(10) PRIMARY KEY,
    exchange VARCHAR(10),
    multiplier DECIMAL(10,5) DEFAULT 1,
    margin DECIMAL(10,5) DEFAULT NULL,
    expiry DATE DEFAULT NULL,
    roll_date DATE DEFAULT NULL,
    active BOOL DEFAULT TRUE,
    FOREIGN KEY(underlying_id) REFERENCES underlying(underlying_id) ON DELETE CASCADE
);

ALTER TABLE underlying
ADD FOREIGN KEY(active_contract)
REFERENCES contract(local_symbol)
ON DELETE SET NULL

CREATE TABLE time_series (
    local_symbol VARCHAR(10),
    dt DATE,
    open_px DECIMAL(10, 5),
    high_px DECIMAL(10, 5),
    low_px DECIMAL(10, 5),
    close_px DECIMAL(10, 5), 
    volume INT DEFAULT NULL,
    open_int INT DEFAULT NULL,
    bid DECIMAL(10,5) DEFAULT NULL,
    ask DECIMAL(10,5) DEFAULT NULL,
    PRIMARY KEY(local_symbol, dt),
    FOREIGN KEY(local_symbol) REFERENCES contract(local_symbol)
); 

CREATE TABLE account (
    dt DATE,
    account_code VARCHAR(9),
    portfolio_value DECIMAL(13,5),
    realised_pnl DECIMAL(13,5),
    unrealised_pnl DECIMAL(13,5),
    margin DECIMAL(13,5) DEFAULT 0,
    PRIMARY KEY(dt, account_code)
);

CREATE TABLE positions (  
    dt DATE, 
    account_code VARCHAR(9),
    local_symbol VARCHAR(10),
    pos INT NOT NULL,
    avg_cost DECIMAL(13,5),
    PRIMARY KEY(dt, account_code, local_symbol),
    FOREIGN KEY(local_symbol) REFERENCES contract(local_symbol)
);

CREATE TABLE transactions (
    dt TIMESTAMP,
    account_code VARCHAR(9),
    local_symbol VARCHAR(10),
    trade_size INT NOT NULL CHECK (trade_size != 0),
    fill_px DECIMAL(13, 5),
    PRIMARY KEY(dt, local_symbol),
    FOREIGN KEY(local_symbol) REFERENCES contract(local_symbol)
);  