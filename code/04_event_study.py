"""
04_event_study.py

Market-model event study around SVB's failure. For each v0 bank:
    1. Estimate  r_bank = alpha + beta * r_SPY  on daily returns in calendar 2022
       (estimation window ends before 2023, so it is untouched by the event).
    2. Abnormal return on each event day = actual return - (alpha + beta * r_SPY).
    3. car_0_2 = sum of abnormal returns on trading days 0, +1, +2:
       Mar 9, Mar 10 and Mar 13, 2023 (day 0 = Mar 9; see DECISIONS.md).

Inputs : inputs/prices/yfinance_prices.csv   (code/03_download_prices.py)
         inputs/prices/crsp/*.csv            CRSP daily returns for delisted banks (optional;
                                             see inputs/prices/crsp/README.md)
Output : outputs/car_0_2.csv                 one row per v0 ticker (12 rows)

SIVB stopped trading on Mar 10, 2023 (the bank was seized before the open).
Its CAR therefore covers only the days it traded; n_event_days records how many.
"""

from pathlib import Path

import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
PRICES = ROOT / "inputs" / "prices"
EVENT_DAYS = pd.to_datetime(["2023-03-09", "2023-03-10", "2023-03-13"])  # days 0, +1, +2
EST_START, EST_END = pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")
MIN_EST_DAYS = 200  # a bank needs most of 2022 to estimate a reliable beta

tickers = pd.read_csv(ROOT / "inputs" / "links" / "v0_banks.csv")["ticker"].tolist()

# 1. Yahoo returns: daily percent change in adjusted close, per ticker.
yf_prices = pd.read_csv(PRICES / "yfinance_prices.csv", parse_dates=["date"])
yf_prices = yf_prices.sort_values(["ticker", "date"])
yf_prices["ret"] = yf_prices.groupby("ticker")["adj_close"].pct_change()
returns = yf_prices.dropna(subset=["ret"])[["date", "ticker", "ret"]]
returns["source"] = "yfinance"

# 2. CRSP returns for banks Yahoo does not have (delisted). WRDS exports name the
#    columns either date/TICKER/RET (classic format) or DlyCalDt/Ticker/DlyRet (new format).
crsp_files = sorted((PRICES / "crsp").glob("*.csv"))
if crsp_files:
    crsp = pd.concat([pd.read_csv(f, dtype=str) for f in crsp_files])
    crsp.columns = crsp.columns.str.lower()
    crsp = crsp.rename(columns={"dlycaldt": "date", "dlyret": "ret"})
    crsp["date"] = pd.to_datetime(crsp["date"])
    crsp["ret"] = pd.to_numeric(crsp["ret"], errors="coerce")  # CRSP uses letter codes for missing returns
    crsp = crsp.dropna(subset=["ret"])
    crsp = crsp[crsp["ticker"].isin(tickers) & ~crsp["ticker"].isin(returns["ticker"])]
    crsp = crsp[["date", "ticker", "ret"]].drop_duplicates()
    crsp["source"] = "CRSP"
    returns = pd.concat([returns, crsp])
assert not returns.duplicated(["date", "ticker"]).any()

# 3. Put each bank's return next to the market (SPY) return on the same day.
market = returns[returns["ticker"] == "SPY"][["date", "ret"]].rename(columns={"ret": "mkt_ret"})
assert set(EVENT_DAYS) <= set(market["date"]), "an event day is not a trading day in the SPY data"
banks = returns[returns["ticker"] != "SPY"].merge(market, on="date", how="inner", validate="m:1")

# 4. For each ticker: fit the market model on 2022, then sum abnormal returns on event days.
rows = []
for ticker in tickers:
    bank = banks[banks["ticker"] == ticker]
    if bank.empty:
        rows.append({"ticker": ticker, "note": "no return data (delisted; add CRSP file)"})
        continue

    est = bank[(bank["date"] >= EST_START) & (bank["date"] <= EST_END)]
    assert len(est) >= MIN_EST_DAYS, f"{ticker}: only {len(est)} estimation days"
    fit = sm.OLS(est["ret"], sm.add_constant(est["mkt_ret"])).fit()
    alpha, beta = fit.params["const"], fit.params["mkt_ret"]

    event = bank[bank["date"].isin(EVENT_DAYS)]
    abnormal = event["ret"] - (alpha + beta * event["mkt_ret"])
    note = "" if len(event) == 3 else f"traded on {len(event)} of 3 event days"

    rows.append({"ticker": ticker, "source": bank["source"].iloc[0],
                 "alpha": alpha, "beta": beta, "n_est_days": len(est),
                 "n_event_days": len(event), "car_0_2": abnormal.sum(), "note": note})

car = pd.DataFrame(rows)
car[["n_est_days", "n_event_days"]] = car[["n_est_days", "n_event_days"]].astype("Int64")  # whole numbers, blank if missing
assert car["ticker"].is_unique and len(car) == len(tickers) == 12

out = ROOT / "outputs" / "car_0_2.csv"
car.to_csv(out, index=False)
print(f"Wrote {out.relative_to(ROOT)}")
print(car.round(4).to_string(index=False))
