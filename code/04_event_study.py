"""
04_event_study.py

Market-model event study around SVB's failure. For each v0 bank:
    1. Estimate  r_bank = alpha + beta * r_SPY  on daily returns in calendar 2022
       (estimation window ends before 2023, so it is untouched by the event).
    2. Abnormal return on each event day = actual return - (alpha + beta * r_SPY).
    3. car_0_2 = sum of abnormal returns on trading days 0, +1, +2:
       Mar 9, Mar 10 and Mar 13, 2023 (day 0 = Mar 9; see DECISIONS.md).

Inputs : inputs/prices/crsp/crsp_dsf.csv          CRSP daily returns      (code/03_download_crsp.py)
         inputs/prices/crsp/crsp_delist.csv       CRSP delisting returns  (same script)
         inputs/prices/crsp/crsp_permno_map.csv   ticker -> PERMCO -> PERMNO (same script)
Output : outputs/car_0_2.csv                      one row per v0 ticker (12 rows), source = CRSP

All returns, banks and SPY, come from CRSP via WRDS. Rows are matched by PERMNO,
never by ticker. Days with no trade (CRSP price < 0) are dropped. SIVB stopped
trading after Mar 9, 2023 (halted Mar 10, then seized; CRSP's Mar 10 return is a
quote, not a trade), so its CAR covers day 0 only; n_event_days and note record this.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
CRSP = ROOT / "inputs" / "prices" / "crsp"
EVENT_DAYS = pd.to_datetime(["2023-03-09", "2023-03-10", "2023-03-13"])  # days 0, +1, +2
EST_START, EST_END = pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")
SAMPLE_END = pd.Timestamp("2023-06-30")  # last day pulled by code/03_download_crsp.py
MIN_EST_DAYS = 200  # a bank needs most of 2022 to estimate a reliable beta

tickers = pd.read_csv(ROOT / "inputs" / "links" / "v0_banks.csv")["ticker"].tolist()

# 1. The PERMNO for each ticker (12 banks + SPY), found by 03 through the PERMCO.
pmap = pd.read_csv(CRSP / "crsp_permno_map.csv")
assert pmap["permno"].is_unique and pmap["ticker"].is_unique
assert set(pmap["ticker"]) == set(tickers) | {"SPY"}

# 2. CRSP daily returns. RET includes dividends.
daily = pd.read_csv(CRSP / "crsp_dsf.csv", parse_dates=["date"])
assert not daily.duplicated(["permno", "date"]).any()

# Keep only days with an actual trade. CRSP marks a no-trade day with a negative
# price (the bid/ask midpoint); a quote nobody traded at is not a market reaction.
# This drops one row: SIVB on Mar 10, 2023 (halted all day; quote-based RET -62.9%).
no_trade = daily["prc"] < 0
print(f"Dropping {no_trade.sum()} no-trade day(s):")
print(daily.loc[no_trade, ["permno", "date", "ret", "prc"]].to_string(index=False))
daily = daily[~no_trade][["permno", "date", "ret"]]

# 3. CRSP delisting returns: the return from the last price to the value after
#    delisting, dated on the delisting date. Keep those inside the sample window.
delist = pd.read_csv(CRSP / "crsp_delist.csv", parse_dates=["dlstdt"])
delist = delist.dropna(subset=["dlret"]).rename(columns={"dlstdt": "date"})
delist = delist[delist["date"] <= SAMPLE_END][["permno", "date", "dlret"]]
assert delist["permno"].is_unique

# 4. Combine them: on a delisting date, compound the day's return with the
#    delisting return; if the stock did not trade that day, use DLRET alone.
rets = daily.merge(delist, on=["permno", "date"], how="outer", validate="1:1")
both = rets["ret"].notna() & rets["dlret"].notna()
rets["ret"] = np.where(both, (1 + rets["ret"]) * (1 + rets["dlret"]) - 1,
                       rets["ret"].fillna(rets["dlret"]))
rets["has_dlret"] = rets["dlret"].notna()
rets = rets.dropna(subset=["ret"])

# 5. Attach tickers by PERMNO (every PERMNO pulled must be in the map).
rets = rets.merge(pmap[["permno", "ticker"]], on="permno", how="left", validate="m:1")
assert rets["ticker"].notna().all()

# 6. Put each bank's return next to the market (SPY) return on the same day.
market = rets[rets["ticker"] == "SPY"][["date", "ret"]].rename(columns={"ret": "mkt_ret"})
assert set(EVENT_DAYS) <= set(market["date"]), "an event day is not a trading day in the SPY data"
banks = rets[rets["ticker"] != "SPY"].merge(market, on="date", how="inner", validate="m:1")

# 7. For each ticker: fit the market model on 2022, then sum abnormal returns on event days.
rows = []
for ticker in tickers:
    bank = banks[banks["ticker"] == ticker]
    assert not bank.empty, f"{ticker}: no CRSP returns"

    est = bank[(bank["date"] >= EST_START) & (bank["date"] <= EST_END)]
    assert len(est) >= MIN_EST_DAYS, f"{ticker}: only {len(est)} estimation days"
    fit = sm.OLS(est["ret"], sm.add_constant(est["mkt_ret"])).fit()
    alpha, beta = fit.params["const"], fit.params["mkt_ret"]

    event = bank[bank["date"].isin(EVENT_DAYS)]
    abnormal = event["ret"] - (alpha + beta * event["mkt_ret"])

    # Say plainly when a CAR covers fewer than 3 days or includes a delisting return.
    notes = []
    if len(event) < 3:
        days = ", ".join(f"day {EVENT_DAYS.get_loc(d)}" for d in event["date"])
        notes.append(f"returns on {len(event)} of 3 event days ({days}); stopped trading")
    if event["has_dlret"].any():
        notes.append("includes CRSP delisting return")

    rows.append({"ticker": ticker, "permno": bank["permno"].iloc[0], "source": "CRSP",
                 "alpha": alpha, "beta": beta, "n_est_days": len(est),
                 "n_event_days": len(event), "car_0_2": abnormal.sum(), "note": "; ".join(notes)})

car = pd.DataFrame(rows)
assert car["ticker"].is_unique and len(car) == len(tickers) == 12
assert car["car_0_2"].notna().all()

out = ROOT / "outputs" / "car_0_2.csv"
car.to_csv(out, index=False)
print(f"Wrote {out.relative_to(ROOT)}")
print(car.round(4).to_string(index=False))
