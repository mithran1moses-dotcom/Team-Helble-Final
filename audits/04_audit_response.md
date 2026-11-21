# Response to the instructor audit (Checkpoint 2)

Replies to `audits/03_instructor_audit.md` (audited commit `30aa41c`). Each finding is marked **fixed** (with the commit), **disputed** (with the reason), or **open / disclosed** (where it is written down, and the plan).

Draft started 2026-11-21 by Lucas Koranda with Claude Code, on branch `v0-pipeline` (PR #9). Riley (D in the v1 plan) owns this file and finishes it.

| ID | Finding | Status | Where |
|---|---|---|---|
| A1 | SIVB is the event and also an observation, with a one-day CAR | **Fixed** | commit `6459083` |
| A2 | Normal p-values and HC1 at small N | **Fixed** | commit `6459083` |
| A3 | Proposal placeholder; "today" screen shows 2022 | **Open**, with a plan | below |
| A4 | Call-report download not scripted; versions not pinned | **Open**, with a plan | below |

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

## A3 · Open: proposal hypothesis and the "today" screen

**Still true today:**
- `PROPOSAL.md:23` still reads "TEAM HYPOTHESIS AND THOUGHTS".
- The fragility screen in `app.py` still filters the 12 v0 banks on 12/31/2022 measures.

**Plan:**
1. **Hypothesis.** The team writes the hypothesis section itself, not an agent, as HW8 asks. Owner: Riley, with the team.
2. **"Today" screen:**
   - Download the latest call reports (09/30/2026), using the script from A4.
   - Run `code/02_build_bank_measures.py` on them → `outputs/bhc_measures_latest.csv`.
   - Point the screen at that file and show its report date.
   - Add a note that CMA merged into FITB in Feb 2026. That explanation is in PR #6, `audits/02_external_findings.md`, not yet merged.
   - Owners: Lucas (download and measures), Mithran (dashboard).

**Target:** the Nov 24 working groups. If it isn't done then, it will be listed as open in the v1 self-audit.

## A4 · Open: scripted call-report download and pinned versions

**Still true today:**
- `inputs/call_reports/README.md` still describes a manual download.
- `requirements.txt` still has unpinned versions (`pandas>=2.0`, bare `numpy`, `wrds`, `statsmodels`, `matplotlib`).

**Plan:**
1. **Download script.** Add `code/00_download_call_reports.py`, using the ASP.NET form fields the audit lists (`ListBox1`, `DatesDropDownList`, `FormatType=TSVRadioButton`, `TabStrip1$Download_0`). It pulls 12/31/2022 and the latest quarter, and is added to `run_all.py --download`. Owner: Lucas.
2. **Pinned versions.** Pin `requirements.txt` with `pip freeze` from a clean environment that runs `run_all.py` and `app.py`. Streamlit stays ≥ 1.49 (`app.py` fails on 1.48). Owner: Riley.
3. **Data vintage.** Record in the pull log that our bulk file says "CDR data as of 2026-09-15". That means it already includes any amendments filed after Mar 9, 2023. This is self-audit finding 10, confirmed in PR #6. The amendments check (POR "last updated" dates for every filer) is in the v1 plan, task 6. Owner: Lucas.

**Target:** the Nov 24 working groups.

## Also from the audit

- **CAR hand check.** We cite the auditor's yfinance check as the hand check our self-audit listed as open (finding 9). It reproduces `car_0_2` to 4 decimals for the 10 banks still on Yahoo; for example, KEY is −0.3347 there vs −0.3348 here. A spreadsheet recomputation of KEY from CRSP is still planned (v1 plan, task 9).
- **PR #6 (external findings).** Still open. Plan:
  - merge it;
  - replace the trade-press links with the FDIC letter of Jul 24, 2023 and Comerica's 8-K;
  - have a person sign the "reviewed by" line.
  - Owner: Riley.

## Not yet done for v1

The full-sample run (about 100 banks) is not in the repo yet. Everything above is still on the 12 v0 banks. The v1 plan (`docs/internal/v1_plan_nov17_to_nov21.md`) has the filters, the owners and the steps.
