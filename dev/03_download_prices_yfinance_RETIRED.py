"""
03_download_prices_yfinance_RETIRED.py  (RETIRED 2026-11-09: kept for reference only)

Not run by run_all.py. Stock returns now come from CRSP via WRDS for all 12 banks
(code/03_download_crsp.py; DECISIONS.md, "Data source"). Needs `pip install yfinance`,
which is no longer in requirements.txt.

Original description:

Downloads daily prices from Yahoo Finance (yfinance) for the 12 v0 banks plus SPY
(the market index for the event study), Jan 2022 to Jun 2023.

Output: inputs/prices/yfinance_prices.csv            long format: date, ticker, adj_close
        inputs/prices/yfinance_prices.provenance.txt  when, what version, which tickers were missing

The raw prices are committed (not git-ignored) because Yahoo revises adjusted
prices over time, so a re-download may not match exactly. Re-running this
script overwrites the snapshot; do that on purpose only.

Delisted tickers (SIVB, CMA) are not on Yahoo. Their returns come from CRSP
instead: see inputs/prices/crsp/README.md.
"""

from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inputs" / "prices" / "yfinance_prices.csv"
START, END = "2022-01-01", "2023-07-01"  # yfinance's end date is exclusive, so this ends Jun 30, 2023

# The 12 v0 tickers come from the link inputs, plus SPY for the market model.
tickers = pd.read_csv(ROOT / "inputs" / "links" / "v0_banks.csv")["ticker"].tolist() + ["SPY"]

# Download adjusted closes (adjusted for splits and dividends, so the
# day-to-day change is the total return).
raw = yf.download(tickers, start=START, end=END, auto_adjust=False, progress=False)
prices = raw["Adj Close"]

# Reshape to one row per (date, ticker) and drop tickers/days with no price.
long = prices.reset_index().melt(id_vars="Date", var_name="ticker", value_name="adj_close")
long = long.dropna(subset=["adj_close"]).rename(columns={"Date": "date"})
long["date"] = pd.to_datetime(long["date"]).dt.date
assert not long.duplicated(["date", "ticker"]).any()

# Record which tickers came back empty, so nobody mistakes a gap for a zero return.
missing = sorted(set(tickers) - set(long["ticker"]))
assert "SPY" not in missing, "no market index data: stop"

OUT.parent.mkdir(parents=True, exist_ok=True)
long.sort_values(["ticker", "date"]).to_csv(OUT, index=False)
OUT.with_name("yfinance_prices.provenance.txt").write_text(
    f"Source: Yahoo Finance via yfinance {yf.__version__}, field 'Adj Close'\n"
    f"Requested: {', '.join(tickers)}\n"
    f"Window: {START} to {END} (end exclusive)\n"
    f"Downloaded: {date.today()}\n"
    f"Rows: {len(long)}\n"
    f"Tickers with no data (delisted; use CRSP): {', '.join(missing) or 'none'}\n")

print(f"Wrote {OUT.relative_to(ROOT)}: {len(long)} rows, {long['ticker'].nunique()} tickers")
print(f"No data for: {missing}")
