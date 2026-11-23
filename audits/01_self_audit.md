# Self-audit 01 (v0 checkpoint)

First written 2026-11-07 by Mithran Moses with Claude Code. Restructured to the HW8 format on 2026-11-14 by Lucas Koranda with Claude Code, on branch `lucas-fundamentals-checks`.

HW8 asks for three things: (A) what a skeptical review of the repo flagged and which findings are real, (B) what this PR fixes and what is still open, with a plan, and (C) the 10-point checklist from `00_PROJECT_SEEDS`. Part D keeps the detailed evidence tables from the first version.

## A. Skeptical review: what it flagged

Part A has two passes. **A1** (findings 1–19) is a broad red-team of the repo by Claude Code on 2026-11-14. **A2** (findings 20–27) is the exact _Skeptical review_ prompt from the course Quick Reference (`FIN331_Quick_Reference.pdf`, starter prompt #5), run on 2026-11-14 after A1's fixes.

### A1. Broad red-team (2026-11-14)

What was rerun on 2026-11-14: the fake-data test (`dev/check_fake_bhc_measures.py`, passes) and `code/05` and `code/06`, which reproduce the committed `outputs/` (differences only in the 15th decimal place and the timestamp in `regression_main.txt`). Steps `02`–`04` could not be rerun on this machine: the raw call reports and CRSP files are not on it.

| # | Finding | Real? | Status |
|---|---|---|---|
| 1 | **The proposal's method section disagrees with the code.** It says N ≈ 350 (the repo says about 100), a Mar 8–15 window and "three trading days from March 8–10" (the code uses Mar 9, 10, 13), a Fama-French 3-factor + KBW model estimated to Feb 28, 2023 (the code uses a market model vs. SPY on 2022), Tier 1 capital as the loss-ratio denominator (the code uses equity + AFS loss), HC3 errors (the code uses HC1), and controls the code doesn't have. | Real | Open (B2) |
| 2 | **The proposal's threats table claims checks that weren't done:** "banks under $1B are excluded" (no such filter), link checks "against SEC 10-K filings" (we used NIC and FDIC records), regressions "with and without SIVB" (not in `specs_tried.md`). | Real | Open (B2) |
| 3 | The proposal has a blank placeholder ("TEAM HYPOTHESIS AND THOUGHTS") and no heading on the dashboard-mockup section. | Real | Open (B2) |
| 4 | The proposal was a notebook (`TeamHelbleProposal.ipynb`) with the mockup embedded inside it; HW8 asks for `PROPOSAL.md` with images saved as files in the repo. | Real | Fixed (B1) |
| 5 | **The dashboard was not live on the web**; the README said "hosted link TBD". | Real | Fixed 11/14 (B1) |
| 6 | `app.py` crashes on Streamlit 1.48 and older (`width="content"` at line 96), and `requirements.txt` did not set a version. | Real | Fixed (B1) |
| 7 | This audit said `n_est_days` = 250; `outputs/car_0_2.csv` says 251. | Real (docs only) | Fixed (B1) |
| 8 | **SIVB is in the regression with a one-day CAR, and it is the failing bank itself.** It has by far the largest loss ratio (0.98) and uninsured share (0.94), so with N = 12 it can drive the slopes. | Real | Open (B2) |
| 9 | **No independent hand check of a CAR.** Steps 01 (link table) and 02 (measures, fake data and MDRM check) have one; step 04 (event study) does not. | Real | Open (B2) |
| 10 | **Call report amendments.** The FFIEC bulk files we downloaded in Nov 2026 show the latest amended values. If a bank amended its 12/31/2022 report after Mar 9, 2023, we use numbers the market did not have. | Real (checked 11/21: 9 of 12 holding companies; `audits/amendments_check.md`) | Open (B2) |
| 11 | Summing subsidiaries' equity is not the holding company's equity (parent-level debt and non-bank units are missing); the FR Y-9C has the consolidated holding-company numbers. | Real, disclosed ("Entity mismatch" in README) | Limitation; v1 comparison planned (B2) |
| 12 | The CAR is measured against SPY, so it includes the move of the whole banking sector; the level of a CAR is not bank-specific. In a cross-sectional regression a shared shock mostly moves the intercept. | Real but minor | Limitation; robustness planned (B2) |
| 13 | With 12 banks and 4 coefficients, the regression is a pipeline check, not evidence; only log assets is significant (p < 0.01; `outputs/regression_main.csv`), and the R² of 0.73 should not be read as fit. | Real, disclosed | Limitation until v1 |
| 14 | Zions has a negative HTM loss (AFS-to-HTM transfer losses sit in AOCI, not in HTM cost minus fair value). | Real | Limitation; robustness check done 11/14 (B2) |
| 15 | A full rebuild needs a WRDS login and two manual downloads, so an auditor without WRDS cannot rerun `code/03`. | Real, disclosed | Limitation (license) |
| 16 | Look-ahead in timing: the 12/31/2022 call reports were due 30 days after quarter end (35 for banks with multiple foreign offices), so by early Feb 2023, before the event; the market model is fit on 2022 only. | Not a problem | OK |
| 17 | Survivorship and ticker reuse: returns are from CRSP (which keeps delisted SIVB and CMA), matched by PERMNO through the PERMCO, never by ticker. | Not a problem | OK |
| 18 | Merges: every merge uses `validate=` and keys are asserted unique (`code/02`, `04`, `05`). | Not a problem | OK |
| 19 | LLM leakage: no LLM produces data, labels or estimates; coding agents only wrote code, which is tested on fake data with hand-computed answers. | Not applicable | OK |

### A2. The exact Skeptical review prompt (rerun 2026-11-14)

Prompt, verbatim: _"Review this repo like a skeptical finance professor. Look for look-ahead bias and leakage, merges without validate, unit and frequency mismatches, hard-coded paths or keys, and steps that don't reproduce from run_all.py. List issues ranked by severity; don't fix anything yet."_

Run by Mithran Moses with Claude Code on branch `v0-pipeline`, after the fixes in part B1. To check reproduction, `python run_all.py` was rerun from the inputs on disk: every file in `outputs/` came back identical except the clock time printed in the two `regression_*.txt` summaries. Findings, most severe first. Items A1 already covers are not repeated (SIVB's one-day CAR is finding 8; call report amendments are finding 10).

| # | Finding | Real? | Status |
|---|---|---|---|
| 20 | **Look-ahead in the sample itself.** The 12 v0 banks were hand-picked after the event, including SIVB and regionals chosen because they "got hit hard" (`docs/internal/v0_plan_nov3_to_nov9.docx`). Picking banks on the outcome can build the result into the sample. | Real, disclosed (`DECISIONS.md`, "For the report") | Open: v1 uses every listed bank that passes fixed filters, set before looking at CARs (B2) |
| 21 | **Unit mismatch in the uninsured share.** The numerator (RCON5597) comes only from subsidiaries with at least $1B in assets, but the denominator (RCON2200) sums every subsidiary, so JPM, CMA and WFC have a slightly understated share. | Real, disclosed (README threats, part D3) | Open: v1 robustness using reporting subsidiaries only (B2) |
| 22 | **`python run_all.py --download` stops at step 01b.** The link table is now hand-checked, and `code/01b_build_link_table.py` refuses to overwrite a checked table, so the download path crashes. The default `python run_all.py` is not affected. | Real | Open (B2) |
| 23 | Frequency: the market model is fit on daily 2022 returns and the CAR sums daily abnormal returns, both from CRSP `ret` with dividends, for banks and SPY alike. No mix of frequencies. | Not a problem | OK |
| 24 | Units: dollar amounts are in $ thousands everywhere (call reports), and every ratio divides thousands by thousands. `log_total_assets` is the log of thousands, which shifts only the intercept. | Not a problem | OK |
| 25 | Merges: every merge in `code/` (`01b`, `02`, `03`, `04`, `05`) uses `validate=`, and keys are asserted unique. The only `how="outer"` merges (call report schedule parts in `02`, delisting returns in `04`) are validated 1:1. | Not a problem | OK |
| 26 | Hard-coded paths or keys: none. Paths are built from the repo root. The WRDS login is typed at a prompt and never saved; `.env` and raw WRDS and call report files are git-ignored. | Not a problem | OK |
| 27 | Reproduction: `python run_all.py` rebuilds every output from the inputs on disk, byte for byte apart from the timestamps (rerun 2026-11-14). A rebuild from nothing still needs WRDS and two manual downloads (finding 15). | Not a problem | OK |

## B. Fixed in this PR, and still open

### B1. Fixed in this PR

- Link table hand-checked, 21 of 21 rows (NIC, and FDIC 12/31/2022 records for closed banks): `audits/link_check_sheet.md`.
- MDRM codes checked against the Fed data dictionary: `audits/mdrm_check.md`.
- Repo tidied: course and planning documents moved to `docs/`.
- Proposal converted to `PROPOSAL.md`; mockup saved as `images/dashboard_mockup.png` (finding 4).
- `requirements.txt` now requires `streamlit>=1.49`, checked against 1.48 (fails), 1.49, 1.50 and 1.67 (all four tabs render, no errors) (finding 6).
- `n_est_days` corrected to 251 in this audit (finding 7).
- This audit restructured to the HW8 format.
- Dashboard live at https://team-helble-final.streamlit.app/, linked at the top of the README (finding 5). First deployed from Lucas's fork (Streamlit Community Cloud needs repo admin); redeployed by Mithran from the team repo's `main` on 11/14, so it updates after each merge.

### B2. Still open, with the plan

| Item | Plan | Who / when |
|---|---|---|
| Proposal disagrees with the code, claims checks not done, has a blank section (findings 1–3) | The team edits `PROPOSAL.md` so the method and threats match the repo, or says clearly what is planned for v1 and not yet done. Fill in the hypothesis section. Written by the team, not an agent (HW8). | Team, before submitting HW8 (Nov 14) |
| Dashboard runs from Lucas's fork, not the team repo | Done 11/14: Mithran redeployed from the team repo (`main`, `app.py`) at https://team-helble-final.streamlit.app/; all 4 tabs checked. | Done |
| Skeptical review prompt | Done 11/14: exact prompt rerun, findings 20–27 in part A2. | Done |
| Sample picked on the outcome (finding 20) | v1: take every listed bank that passes filters fixed in advance (assets, trading history, liquidity), log the filters in `specs_tried.md` before running the regression. | v1, Nov 21 |
| Uninsured share numerator vs denominator (finding 21) | v1 robustness: compute the share over reporting subsidiaries only and compare. | v1, Nov 21 |
| `run_all.py --download` stops at 01b (finding 22) | Take 01b out of the download steps (the link table is a hand-checked input now), or let 01b skip when a checked table exists. | Before v1, Nov 21 |
| SIVB drives the regression (finding 8) | In v1, report the main spec with and without SIVB and log both in `specs_tried.md`. | v1, Nov 21 |
| No hand check of a CAR (finding 9) | Recompute one bank's `car_0_2` (e.g. KEY) by hand in a spreadsheet from its CRSP rows and SPY, and record it in `audits/`. | v1, Nov 21 |
| Call report amendments (finding 10) | **Checked 11/21** (`dev/check_amendments.py`, `audits/amendments_check.md`): the main bank of 9 of 12 holding companies resubmitted its 12/31/2022 report after Mar 9, 2023 (all after the FDIC letter of Jul 24, 2023); 41% of all filers ≥ $1B did. The file shows when, not what changed. Next: flag in the data, a robustness row without them, and a search for as-filed values. | Lucas, Nov 24 |
| Subsidiary sum vs. holding-company equity (finding 11) | Compare total equity and assets to the FR Y-9C for the 12 holding companies and report the gaps. | v1, Nov 21 |
| CAR includes the sector move (finding 12) | Robustness: market model with a bank index next to SPY, logged in `specs_tried.md`. | v1 |
| AFS-to-HTM transfer losses (finding 14) | Decided 11/14: kept as a stated limitation (`DECISIONS.md`). Robustness: main spec without ZION, `outputs/regression_drop_zion.csv` (`specs_tried.md` #5); coefficients barely move. In v1, rerun it and drop any other bank with a negative HTM loss. | Done for v0 (Mithran, 11/14) |
| MDRM check second sign-off | Done 11/14: Mithran reviewed and signed `audits/mdrm_check.md` (script rerun, table and counts match). | Done |

## C. The 10-point checklist (`00_PROJECT_SEEDS`)

| # | Item | Status | One line |
|---|---|---|---|
| 1 | It reproduces | OK, with a caveat | `python run_all.py` rebuilds every output; full rerun matched byte for byte on 11/9, and 05–06 again on 11/14. Needs a WRDS login and two manual downloads. |
| 2 | Every input has a provenance | OK | Source, date and how to get it again: `inputs/call_reports/README.md`, `inputs/links/README.md`, `inputs/prices/crsp/crsp_pull.provenance.txt`. |
| 3 | Unit of observation is right | OK | One row = one bank holding company; `bhc_rssd` asserted unique; every merge uses `validate=`. |
| 4 | No look-ahead | Problem, disclosed | 12/31/2022 call reports and a 2022 estimation window; survivorship handled through CRSP. But for 9 of 12 holding companies the main bank resubmitted its 12/31/2022 report after Mar 9, 2023 (finding 10, `audits/amendments_check.md`). |
| 5 | No LLM leakage | OK | No LLM in the data or the estimates. |
| 6 | No p-hacking | OK | `specs_tried.md` logs all 4 specs run, including the dropped 10-bank one. |
| 7 | Magnitudes, not just stars | Not yet | With N = 12 there is nothing to interpret; v1 will report effects in CAR points per standard deviation of each measure. |
| 8 | Checks by hand | Problem | Link table, measures and MDRM codes are hand-checked; no CAR is recomputed by hand yet (finding 9). |
| 9 | Honest limits | OK | "Threats to validity" in `README.md`; every limitation in this audit is listed there. |
| 10 | You understand it | Not yet | Each teammate walks through one pipeline step for the others before v1. |

## D. Evidence tables (from the first version, 2026-11-07, updated since)

### D1. Data and provenance

| Item | Status | Evidence |
|---|---|---|
| Call reports are from 12/31/2022, the last quarter before SVB failed (no look-ahead) | OK | `inputs/call_reports/README.md` pull log; `report_period` column in `outputs/bhc_measures_2022Q4.csv` |
| Every raw file has a source and download date | OK | pull logs in `inputs/call_reports/README.md`, `inputs/links/README.md`; `inputs/prices/crsp/crsp_pull.provenance.txt` |
| **Stock returns: CRSP via WRDS for all 12 banks and SPY** (switched from yfinance on 11/9 for one consistent source that includes delisted banks). Raw pulls are git-ignored (WRDS license); git history checked on 11/9: no raw CRSP data was ever committed. | OK | `inputs/prices/crsp/crsp_pull.provenance.txt` (source, tables `crsp.stocknames`, `crsp.dsf`, `crsp.dsedelist`, date pulled); `.gitignore`; `DECISIONS.md` "Data source" |
| MDRM codes (2170, 3210, 2200, 5597, 1754, 1771, 1772, 1773) checked against the Federal Reserve MDRM data dictionary for 12/31/2022 | OK (11/11, Lucas; needs a second reviewer's sign-off) | `audits/mdrm_check.md`, rerun with `dev/check_mdrm_codes.py`: all 14 RCFD/RCON codes are in force with the expected names. Spot check: SVB's HTM loss ($15.2B), BAC's ($108.6B) and WFC's ($41.6B) in `outputs/bank_measures_2022Q4.csv` match widely reported figures. |

### D2. Sample

| Item | Status | Evidence |
|---|---|---|
| **Convenience sample chosen knowing the outcome.** The 12 v0 banks were picked after the fact. v1 uses all listed banks. | LIMITATION | `inputs/links/v0_banks.csv`; README threats list |
| **Survivorship.** SIVB, SBNY, FRC, PACW failed or merged; Comerica (CMA) was acquired by Fifth Third. Yahoo had no data for SIVB or CMA; both are now included through CRSP, which keeps delisted stocks. | OK (fixed 11/9) | `outputs/car_0_2.csv` (12 rows, source = CRSP) |
| Exactly 12 holding companies, unique `bhc_rssd` | OK | asserted in `code/05_build_analysis_sample.py`; `outputs/analysis_sample.csv` |
| Regression uses all 12 banks (asserted in `code/06_regression.py`) | OK | `n_obs` and `banks_used` in `outputs/regression_main.csv`; `specs_tried.md` #3 (10-bank run kept as #1) |

### D3. Measures

| Item | Status | Evidence |
|---|---|---|
| **Loss-ratio choice and double counting.** Main = (HTM loss + AFS loss) / (total equity + AFS loss). AFS losses are already deducted from book equity, so they are added back to the denominator (Jiang, Matvos, Piskorski & Seru 2023). Robustness = HTM loss / equity. | OK | `add_ratios()` in `code/02_build_bank_measures.py` |
| **Holding company vs. subsidiary.** Dollar amounts are summed across each holding company's banks first, then ratios are computed. | OK | `aggregate_to_bhc()` in `code/02_build_bank_measures.py`; tested on fake data with hand-computed answers in `dev/check_fake_bhc_measures.py` |
| **Uninsured deposits (RCON5597) are only reported by banks with at least $1B in assets.** Small subsidiaries add deposits but no uninsured amount, which slightly understates the share. | LIMITATION | `n_banks_uninsured_reported` vs `n_banks` in `outputs/bhc_measures_2022Q4.csv` (affects JPM, CMA, WFC through tiny trust/limited-purpose banks) |
| **AFS-to-HTM transfers.** Losses on securities moved from AFS to HTM stay in equity (AOCI) and are left out of HTM cost minus fair value, so the loss ratio understates fragility for banks that transferred. Zions shows a negative HTM loss. | LIMITATION (decided 11/14); robustness check done | `htm_loss` for ZION in `outputs/bhc_measures_2022Q4.csv`; `outputs/regression_drop_zion.csv`; `DECISIONS.md` |

### D4. Event study

| Item | Status | Evidence |
|---|---|---|
| **Window choice justified against the news timeline.** Days 0 to +2 = Mar 9, 10, 13, 2023: SVB's crash, its seizure, and the Signature closure and backstop. Ends before the Credit Suisse shock on Mar 15. | OK | `DECISIONS.md`; README; `EVENT_DAYS` in `code/04_event_study.py` (asserted to be trading days) |
| Market model vs SPY, estimated on calendar 2022 only (ends before 2023) | OK | `code/04_event_study.py`; `n_est_days` = 251 in `outputs/car_0_2.csv` |
| **SIVB stopped trading after Mar 9, so its CAR covers only day 0.** CRSP lists a Mar 10 return (−62.9%) but its price is negative, meaning a bid/ask quote with no trade; all no-trade days are dropped (only this one row). | OK (handled), LIMITATION (comparability) | `n_event_days` and `note` columns in `outputs/car_0_2.csv`; no-trade filter in `code/04_event_study.py`; `DECISIONS.md` "Data source" |
| CAR is a sum of simple daily abnormal returns; for very large moves (WAL) it is more negative than the compounded loss | LIMITATION | README threats list; buy-and-hold CAR is a possible robustness check |
| **PERMNO matching.** Banks are matched ticker → NY Fed PERMCO → CRSP common-share PERMNO (share code 10/11), never by ticker; SPY fixed as PERMNO 84398 and checked. Exactly one PERMNO per bank is asserted. | OK | `code/03_download_crsp.py`; PERMNOs listed in `inputs/prices/crsp/crsp_pull.provenance.txt` and `permno` column of `outputs/car_0_2.csv` |
| **Delisting returns** from `crsp.dsedelist` are compounded into the return on the delisting date. SIVB's record (Mar 10, 2023, code 584) has no delisting return, so nothing is added; the other banks are still listed. | OK | `code/04_event_study.py`; `inputs/prices/crsp/crsp_delist.csv` (git-ignored) |
| One return source: CRSP `ret` (includes dividends) for all banks and SPY | OK | `source` column in `outputs/car_0_2.csv` |

### D5. Merges and keys

| Item | Status | Evidence |
|---|---|---|
| Every merge uses `validate=` and keys are asserted unique | OK | `code/01b`, `02`, `03`, `04`, `05` |
| **Link quality: match rate and hand-checked sample.** 12 of 12 tickers matched by name to the NY Fed file; 21 linked banks, of which 19 file call reports (the 2 trust companies without a call report are printed and dropped). Rows hand-checked: **21 of 21**: 14 on NIC (11/11, Lucas) and 7 that NIC can't show on FDIC 12/31/2022 records (11/14, Lucas). | OK (done 11/14) | `audits/link_check_sheet.md`; `checked_by`, `checked_on` in `inputs/links/bank_link_v0.csv`; output of `code/02_build_bank_measures.py` |
| Two linked banks have no NIC record; identified from the call report filer list as Comerica Bank (60143) and MUFG Union Bank (212465, owned by USB 12/1/2022 to 5/26/2023); names filled in the link table | OK (hand-checked 11/14 on FDIC records) | `outputs/bank_measures_2022Q4.csv` |
| Zions is a bank with no holding company (`bhc_rssd` = `bank_rssd`) | OK | note on ZION row of `inputs/links/bank_link_v0.csv` |
| Banks owned by another bank are dropped to avoid double counting (consolidated in the parent's call report) | OK (hand-checked 11/11: findings B and C in `audits/link_check_sheet.md`) | dropped list printed by `code/01b_build_link_table.py` |

### D6. Threats to validity

Kept as a living list in `README.md` ("Threats to validity"). Every item above marked LIMITATION is listed there.

### D7. Reproducibility

| Item | Status | Evidence |
|---|---|---|
| One command rebuilds every output from the inputs | OK | `python run_all.py`. On 2026-11-09, after the switch to CRSP, `outputs/` and `temp/` were emptied and a full rerun reproduced every committed output byte for byte, except the clock time printed inside `outputs/regression_main.txt`. (Uses the CRSP files on disk; pulling them again needs a WRDS login.) |
| Fake-data test runs before real data | OK | first steps of `run_all.py` |
| Manual downloads documented step by step | OK | READMEs in `inputs/call_reports/`, `inputs/links/`; CRSP pull is scripted and needs a WRDS login (`inputs/prices/crsp/README.md`) |
| Every number in the dashboard comes from `outputs/` and names its file | OK | `app.py` |
| Specs logged | OK | `specs_tried.md` (4 entries) |

