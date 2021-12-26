import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from arbitrade.database.database import Database
from arbitrade.controllers.asset_builder import AssetBuilder

def get_log_returns(df):
    log_px = df.apply(np.log)
    log_returns = log_px.diff(1)
    log_returns.dropna(inplace=True)
    return log_returns

def get_spread_series(builder, t1, k1, p1, t2, k2, p2):
    A = builder.build(t1, k1, p1).get_price_series()
    B = builder.build(t2, k2, p2).get_price_series()
    
    merge = A.merge(B, how="inner", on="dt", suffixes=(f" {t1}{p1}", f" {t2}{p2}"))
    merge.set_index("dt", inplace=True)
    df = merge[[f"close_px {t1}{p1}",f"close_px {t2}{p2}"]]
    return df

def apply_linreg(df, constant=True, show=False):
    Y = df.iloc[:,0]
    X = df.iloc[:,1]
    if constant:
        X = sm.add_constant(X)
    model = sm.OLS(Y,X)
    results = model.fit()
    se_regression = np.sqrt(results.mse_resid)

    if show:
        print(results.summary())
        print("\nStandard Error of Regression = ", se_regression, "\n")
    return results

def get_linear_combination(df, beta_coeff, show=False):
    new = df.copy()
    new.iloc[:,1] = df.iloc[:,1].multiply(beta_coeff)
    spread = new.iloc[:,0] + new.iloc[:,1]
    if show:
        spread.plot(xlabel="Datetime (t)", ylabel="Spread (Wt)", title=f"Wt = At + ({beta_coeff})Bt")
        plt.show()
    return spread

def stationarity_test(spread, show=False):
    results = adfuller(spread)
    d = {
        "t-statistic": results[0],
        "p-value": results[1],
        "lags": results[2],
        "num observations": results[3]    
    }
    critical_values = results[4]

    if show:
        print(d)
        print(critical_values)
    return d, critical_values

def get_zero_crossings(spread):
    mu = np.mean(spread)
    normalise = spread.subtract(mu)
    crossings = np.where(np.diff(np.sign(normalise)))[0] + 1
    crossing_intervals = np.diff(crossings)
    return crossing_intervals

def get_statistics(pdf):
    mean = np.mean(pdf)
    stdev = np.std(pdf)
    ci_95 = np.quantile(pdf, [0.025,0.975])
    return {"mean": mean, "stdev": stdev, "95% CI": ci_95}

def bootstrap(pop, function):
    boot_values = []

    for _ in range(1000):
        boot_sample = np.random.choice(pop, replace=True, size=len(pop))
        metric = function(boot_sample)
        boot_values.append(metric)
    
    return np.array(boot_values)

def optimise_threshold(spread, show=False):
    profits_d = {}
    for threshold in np.arange(0, np.std(spread)*3, np.std(spread)/5):
        quantiles = bootstrap(spread, lambda sample: stats.percentileofscore(np.abs(sample), threshold) / 100)
        mean_quantile = np.mean(quantiles)
        profit = (1-mean_quantile) * threshold
        profits_d[threshold] = profit

    if show:
        plt.plot(profits_d.keys(), profits_d.values(), "r")
        plt.suptitle('Profit Function')
        plt.xlabel('Threshold')
        plt.ylabel('Profit')
        plt.show()
    return profits_d

if __name__ == "__main__":
    db = Database()
    db.connect()
    builder = AssetBuilder(db)
    beta_coeff = -1.05

    df = get_spread_series(builder, "ES", "FUT", 0, "ES", "FUT", 1)
    log_returns = get_log_returns(df)
    
    apply_linreg(log_returns)
    
    spread = get_linear_combination(df, beta_coeff)
    stationarity_test(spread)

    crossing_intervals = get_zero_crossings(spread)
    result = bootstrap(crossing_intervals, lambda sample: get_statistics(sample))

    profit_pdf = optimise_threshold(spread, show=True)

    db.disconnect()