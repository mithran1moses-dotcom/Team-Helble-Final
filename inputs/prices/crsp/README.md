# CRSP daily returns (all 12 v0 banks + SPY)

All stock returns in the project come from CRSP via WRDS (see `DECISIONS.md`, "Data source").
`code/03_download_crsp.py` pulls them; `code/04_event_study.py` reads them.

**The CSV files here are git-ignored.** The WRDS license does not allow redistributing CRSP data.
Only this README and the provenance note are committed.

## How to pull

```
pip install wrds
python3 code/03_download_crsp.py
```

The script asks for your WRDS username and password (and WRDS may send a Duo push).
Nothing is saved: no `.pgpass` file, no credentials in code.

## How banks are matched (never by ticker)

ticker → holding-company name (`inputs/links/v0_banks.csv`) → **PERMCO** (NY Fed CRSP-FRB link
file, links valid on 12/31/2022) → **PERMNO** (CRSP `stocknames`, common shares, share code 10/11).
SPY is fixed as PERMNO 84398, checked against `stocknames`.

## Files written

| File | CRSP table | What |
|---|---|---|
| `crsp_names.csv` | `crsp.stocknames` | name, ticker and share-code history for the 13 PERMNOs |
| `crsp_dsf.csv` | `crsp.dsf` | daily `ret` (includes dividends), 2022-01-01 to 2023-06-30 |
| `crsp_delist.csv` | `crsp.dsedelist` | delisting code and delisting return (`dlret`) |
| `crsp_permno_map.csv` | derived | ticker → permco → permno used by `code/04_event_study.py` |
| `crsp_pull.provenance.txt` | – | source, tables, window, date pulled, row counts (committed) |

Delisting returns: `code/04_event_study.py` compounds `dlret` into the return on the delisting date
(or uses it alone if the stock did not trade that day).

**Pull log**

| Files | Pulled on | By | Notes |
|---|---|---|---|
| | | | |
