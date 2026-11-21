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
| 0b | Call-report download script (`code/00_download_call_reports.py`) | Done 11/21 (Lucas, with Claude Code) | Instructor audit A4. Scripted FFIEC form; first step of `run_all.py --download`. Rebuild from it reproduces every committed output |
| 1 | Link table (`inputs/links/bank_link_v0.csv`) | Built 11/7; hand-checked 21/21 (11/14, Lucas) | 21 bank subsidiaries for 12 BHCs. 14 rows checked on NIC, 7 on FDIC 12/31/2022 records (`audits/link_check_sheet.md`). Names for 60143 and 212465 filled by hand |
| 2 | Call-report measures, holding-company level | Done 11/7 | `outputs/bhc_measures_2022Q4.csv`, 12 BHCs from 19 filing banks; fake-data check passes |
| 3 | Returns and event study (`car_0_2`) | Done 11/9 (Mithran, with Claude Code) | Switched to CRSP via WRDS for all 12 banks + SPY (`code/03_download_crsp.py`), replacing yfinance (moved to `dev/`). Matched by PERMNO via PERMCO, not ticker. Delisting returns included (SIVB's record has none). No-trade days dropped, so SIVB's CAR covers day 0 only. `outputs/car_0_2.csv`: 12 of 12 banks, source = CRSP |
| 4 | Merge and regression | Done 11/9 (12 of 12 banks) | `outputs/analysis_sample.csv` (12 rows), regression N=12 asserted, scatter; `specs_tried.md` #3–4 (10-bank run kept as #1) |
| 4b | A1 + A2 fixes (failed banks out of the main spec, HC3 with t p-values) | Done 11/21 (Lucas, with Claude Code) | `failed_in_window` column in `analysis_sample.csv`; main spec N=11; with-SIVB run in `code/06c`; `specs_tried.md` #6–9; dashboard shows both. Still on the 12 v0 banks, not the full sample |
| 5 | Streamlit dashboard (`app.py`) | Done 11/7; live 11/14 | 4 tabs, reads only outputs/. Live at https://team-helble-final.streamlit.app/, deployed 11/14 by Mithran from the team repo (`main`, `app.py`); all 4 tabs checked in a browser. Lucas's earlier deploy from his fork (https://team-helble-final-v0.streamlit.app/) is no longer the official link. |
| 5b | "Today" screen on the latest quarter (instructor audit A3) | Done 11/21 (Lucas, with Claude Code) | 09/30/2026 call reports via `code/00`; `02` builds `outputs/bhc_measures_2026Q3.csv` (10 holding companies; SIVB, CMA dropped). Screen defaults to it and shows the report date; 12/31/2022 view with CARs kept |
| 6 | `run_all.py` and self-audit | Done 11/7; updated 11/9, 11/11, 11/14 | full rerun on 11/9 reproduces committed outputs; 05–06 rerun again on 11/14. Self-audit restructured to the HW8 format on 11/14 (Lucas, with Claude Code); open items with plans in its part B2 |
| 7 | Proposal (`PROPOSAL.md`) | Draft 11/14 (team) | Converted from the notebook on 11/14. Method and threats sections still disagree with the code; team to edit (self-audit findings 1–3) |

## Blocked / waiting on

- Nothing blocked. MDRM code check (`audits/mdrm_check.md`) signed off by Mithran on 11/14.

## Next up

- Fill in the hypothesis section of `PROPOSAL.md` (facts fixed to match the repo on 11/14).
- Skeptical review prompt rerun 11/14 (self-audit part A2). New open items: sample picked on the outcome, uninsured-share mismatch, `run_all.py --download` stops at 01b (plans in part B2).
- v1 items with plans: `audits/01_self_audit.md` part B2.
