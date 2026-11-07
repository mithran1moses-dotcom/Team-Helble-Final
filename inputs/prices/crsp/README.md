# CRSP daily returns for delisted v0 banks

Yahoo Finance has no data for **SIVB** (SVB Financial Group) or **CMA** (Comerica), because both are delisted.
Their daily returns come from CRSP instead. `code/04_event_study.py` picks up any CSV in this folder.

**The CSV files here are git-ignored.** The WRDS license does not allow redistributing CRSP data.

## How to export (WRDS)

1. WRDS → CRSP → Stock / Security Files → **Daily Stock File**.
2. Date range: **2022-01-01 to 2023-06-30**.
3. Company codes: **PERMCO**. Enter `9588` (SVB Financial Group) and `1261` (Comerica).
   These PERMCOs come from the NY Fed CRSP-FRB link file (`inputs/links/raw/crsp_20240930v2.csv`).
4. Variables: **TICKER, PERMNO, PERMCO, RET** (keep date, which WRDS adds automatically).
5. Output format: **comma-delimited text (.csv)**. Save it in this folder (any file name ending `.csv`).

The script needs the columns `date`, `TICKER` and `RET` (column names in any case).
CRSP's `RET` already includes dividends, matching Yahoo's adjusted-close returns.

**Pull log**

| File | Downloaded on | By | Notes |
|---|---|---|---|
| | | | |
