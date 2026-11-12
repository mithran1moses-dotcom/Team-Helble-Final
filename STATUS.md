# Status

Update this whenever a pipeline step is finished or blocked. Add the date and your name.

## Deadlines (from DECISIONS.md)

- v0 checkpoint + proposal (HW8): Sat Nov 14
- v1 full-sample results: Sat Nov 21
- Working groups fix audit findings: Tue Nov 24
- Presentations: Dec 1 / Dec 3

## Pipeline steps

| Step | What | Status | Notes |
|---|---|---|---|
| 0 | Setup files (CLAUDE.md, README, logs) | Done 11/7 (Mithran, with Claude Code) | README matches DECISIONS.md |
| 1 | Link table (`inputs/links/bank_link_v0.csv`) | Built 11/7, awaiting hand-check | 21 bank subsidiaries for 12 BHCs; 2 rows have no NIC name (60143, 212465) |
| 2 | Call-report measures, holding-company level | Done 11/7 | `outputs/bhc_measures_2022Q4.csv`, 12 BHCs from 19 filing banks; fake-data check passes |
| 3 | Returns and event study (`car_0_2`) | Done 11/9 (Mithran, with Claude Code) | Switched to CRSP via WRDS for all 12 banks + SPY (`code/03_download_crsp.py`), replacing yfinance (moved to `dev/`). Matched by PERMNO via PERMCO, not ticker. Delisting returns included (SIVB's record has none). No-trade days dropped, so SIVB's CAR covers day 0 only. `outputs/car_0_2.csv`: 12 of 12 banks, source = CRSP |
| 4 | Merge and regression | Done 11/9 (12 of 12 banks) | `outputs/analysis_sample.csv` (12 rows), regression N=12 asserted, scatter; `specs_tried.md` #3–4 (10-bank run kept as #1) |
| 5 | Streamlit dashboard (`app.py`) | Done 11/7 | 4 tabs, reads only outputs/; checked all tabs and the screen filters in a browser |
| 6 | `run_all.py` and self-audit | Done 11/7 | full rerun reproduces committed outputs; audit lists 5 open items |

## Blocked / waiting on

- Link-table hand-check: 14 of 21 rows signed (11/11, Lucas). 7 rows (closed banks and non-insured trust companies) await review of their FDIC evidence in `audits/link_check_sheet.md`.

## Next up

- Decide how to treat losses on securities moved from AFS to HTM (Zions shows a negative HTM loss).
