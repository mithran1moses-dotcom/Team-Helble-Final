# Response to the instructor audit (Checkpoint 2)

Replies to `audits/03_instructor_audit.md` (audited commit `30aa41c`). Each finding is marked **fixed** (with the commit), **disputed** (with the reason), or **open / disclosed** (where it is written down, and the plan).

Draft started 2026-11-21 by Lucas Koranda with Claude Code, on branch `v0-pipeline` (PR #9). Riley (D in the v1 plan) owns this file and finishes it.

| ID | Finding | Status | Where |
|---|---|---|---|
| A1 | SIVB is the event and also an observation, with a one-day CAR | **Fixed** | commit `6459083` |
| A2 | Normal p-values and HC1 at small N | **Fixed** | commit `6459083` |
| A3 | Proposal placeholder; "today" screen shows 2022 | **Partly fixed**: screen on 09/30/2026; hypothesis still open | below |
| A4 | Call-report download not scripted; versions not pinned | **Fixed** (amendments check still open) | below |

## A1 · Fixed: failed banks are out of the main regression

**What we changed (commit `6459083`):**
- **Rule written down first.** `DECISIONS.md` ("Failed-bank rule and inference") says that banks that failed inside the event window (Mar 9–13, 2023) are out of the main spec: SIVB (seized Mar 10) and SBNY (closed Mar 12; v1 only). FRC failed May 1, outside the window, so the rule keeps it. The team still has to confirm that before the v1 run.
- **Flag in the data.** `code/05_build_analysis_sample.py` adds a `failed_in_window` column to `outputs/analysis_sample.csv`. It asserts that SIVB is the only failed bank in v0.
- **Main spec without SIVB.** `code/06_regression.py` runs on the 11 other banks and asserts N = 11.
- **With-SIVB run kept as robustness.** `code/06c_robustness_with_failed.py` → `outputs/regression_with_failed.csv`.
- **Logged.** Both runs are in `specs_tried.md` (#6 main, #7 with SIVB). The old no-ZION check now starts from the 11-bank sample (#8, 10 banks).
- **Scatter.** SIVB is still drawn, as a hollow point labeled "failed, not in regression".

**How to see it's fixed:**

| | Main, no SIVB (11) | With SIVB (12) |
|---|---|---|
| `uninsured_dep_share` | −0.153 (p = 0.89) | −0.442 (p = 0.52) |
| `unreal_loss_to_adj_equity` | +0.085 (p = 0.91) | −0.048 (p = 0.92) |
| `log_total_assets` | +0.121 (p = 0.02) | +0.117 (p = 0.01) |

Sources: `outputs/regression_main.csv` and `outputs/regression_with_failed.csv`. Both use HC3 errors with t p-values (A2), so the p-values differ from the audit's HC1 table. The coefficients match the audit's re-estimate in A1 exactly. As the audit says, SIVB alone sets the sign of the loss-ratio slope at this N.

## A2 · Fixed: HC3 errors with t-based p-values

**What we changed (commit `6459083`):**
- `code/06_regression.py`, `06b` and `06c` all use `fit(cov_type="HC3", use_t=True)`.
- Each output table now has a `t_stat` and a `cov_type` column.
- The dashboard's Methodology and Analysis tabs say HC3 with t p-values.

**How to see it's fixed:**
- `outputs/regression_main.txt` reports `Covariance Type: HC3` and t-statistics, with 7 residual degrees of freedom.
- `log_total_assets` goes from p = 0.0001 (HC1, normal) to p = 0.02 (HC3, t₇).

## A3 · Partly fixed: the "today" screen uses the latest quarter; hypothesis still open

**Fixed: the screen shows the latest call reports.**
- `code/00_download_call_reports.py 2026Q3 09/30/2026` pulls the 09/30/2026 call reports (CDR data as of 2026-11-14).
- `code/02_build_bank_measures.py 2026Q3 09302026` builds `outputs/bhc_measures_2026Q3.csv`. Both steps are in `run_all.py`.
- The dashboard's fragility screen opens on "Today: latest call reports (09/30/2026)". The date is read from the file's `report_period` column. The 12/31/2022 view, with each bank's CAR, is one click away.
- **Banks that changed since 2023.** SIVB failed and CMA merged into FITB (Feb 2026), so neither has a filing bank in 09/30/2026. `02` prints and drops them for later quarters; for 2022Q4 it still stops if any holding company is missing. The screen names both. FITB's numbers now include Comerica's (total assets $300B in `bhc_measures_2026Q3.csv`, up from $206B in `bhc_measures_2022Q4.csv`).
- **Limitation, disclosed in the README threats list.** Banks are linked to holding companies as of 12/31/2022, so subsidiaries added since are not captured. Updating this needs NIC relationships as of 2026.

**Still open: the hypothesis.** `PROPOSAL.md:23` still reads "TEAM HYPOTHESIS AND THOUGHTS". The team writes this section itself, not an agent, as HW8 asks. Owner: Riley, with the team. Target: the Nov 24 working groups.

## A4 · Fixed: call-report download scripted; versions pinned

**Fixed: the download is scripted.**
- `code/00_download_call_reports.py` fills in the FFIEC form with the fields the audit lists (`ListBox1`, `DatesDropDownList`, `FormatType=TSVRadioButton`, `TabStrip1$Download_0`). One detail the audit didn't mention: the date list posts back a numeric ID, not the date, so the script looks the ID up from the date text.
- `python code/00_download_call_reports.py 2022Q4 12/31/2022` gets all 51 files in about 2 seconds. It is the first step of `run_all.py --download`.
- Checked on 2026-11-21: we reran `02`, `05` and `06` from the scripted download, and every committed output came out the same (only the clock time in `regression_main.txt` differs). The pull log in `inputs/call_reports/README.md` has the row.
- The same script pulls the latest quarter (`2026Q3 09/30/2026`) for A3.

**Also:**
1. **Pinned versions: fixed.** `requirements.txt` now lists every package at its exact version, from `pip freeze` in a fresh Python 3.11 environment. It includes `requests`, which `code/00` needs and which was missing before. In that environment we reran:
   - the call-report download;
   - the fake-data check;
   - `02` for 2022Q4 and 2026Q3 (outputs byte-identical);
   - `05`, `06`, `06b` and `06c` (outputs match the committed ones to 1e-13);
   - `app.py` (no errors).
   Steps `03`–`04` need WRDS and were not rerun.
2. **Data vintage and amendments.** The pull log now records that our bulk file says "CDR data as of 2026-09-15" (both the Nov 7 and Nov 21 pulls). That means it already includes any amendments filed after Mar 9, 2023. This is self-audit finding 10, confirmed in PR #6. Still open: the amendments check (POR "last updated" dates for every filer), v1 plan task 6. Owner: Lucas.

**Target for the amendments check:** the Nov 24 working groups.

## Also from the audit

- **CAR hand check.** We cite the auditor's yfinance check as the hand check our self-audit listed as open (finding 9). It reproduces `car_0_2` to 4 decimals for the 10 banks still on Yahoo; for example, KEY is −0.3347 there vs −0.3348 here. A spreadsheet recomputation of KEY from CRSP is still planned (v1 plan, task 9).
- **PR #6 (external findings).** Still open. Plan:
  - merge it;
  - replace the trade-press links with the FDIC letter of Jul 24, 2023 and Comerica's 8-K;
  - have a person sign the "reviewed by" line.
  - Owner: Riley.

## Not yet done for v1

The full-sample run (about 100 banks) is not in the repo yet. Everything above is still on the 12 v0 banks. The v1 plan (`docs/internal/v1_plan_nov17_to_nov21.md`) has the filters, the owners and the steps.
