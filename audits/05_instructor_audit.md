# Instructor audit: Team Helble, Checkpoint 3

**Repo:** mithran1moses-dotcom/Team-Helble-Final · **Audited commit:** `61ed6c7` (2026-11-21, head of PR #9, branch `v0-pipeline`, not merged; `main` has no work since Checkpoint 2 beyond merging the CP2 audit) · **Seed:** 6, bank fragility: SVB, and who's next · **CP2 audit:** `audits/03_instructor_audit.md` (commit `30aa41c`)

> Note from your human teacher: This review is generated with minimal supervision from Opus 5.5-high. It is thorough, but can be too generous at times and doesn't know my taste for what is "good". Grades it and I would assign are correlated, but noisy, ok? If you want additional feedback from _me_, you need to find me before/after/during class or during office hours for a guaranteed speedy reply. I will try to respond to emails and issues, but can not respond to student inquiries around the clock across the final weeks of class. Response times will be unpredictable, though during Thanksgiving week, I will do my best to respond quickly virtually, as in person options will be nil.

## Summary

Your CP2 follow-up is careful and it reproduces.
- I reran everything except the CRSP pull from a fresh copy of PR #9, including your new scripted FFIEC download for 12/31/2022 and 09/30/2026. Every output CSV came out identical.
- My own parser of the raw call reports gives the same measures for both quarters. My own OLS with HC3 errors gives the same main regression.
- Three of the four CP2 findings are fixed, and the amendments check is a real piece of self-auditing.

But Checkpoint 3 asked for v1 on the full sample, and the repo is still the 12 v0 banks (your response file says so too). That is the one thing that matters most before Dec 1 (B1). Second: your live dashboard deploys from `main`, and none of this work is on `main` yet (B2).

## Follow-up on your Checkpoint 2 audit

Response file: `audits/04_audit_response.md`, found on PR #9 (branch `v0-pipeline`; not on `main`).

| CP2 finding | Status | Evidence |
|---|---|---|
| A1 · SIVB in the regression | fixed | Commit `6459083`. Fresh rerun of `code/05` and `06`: `outputs/regression_main.csv` has `n_obs` = 11 and no SIVB in `banks_used`. Coefficients: uninsured −0.1528, loss ratio +0.0849, log assets +0.1205, matching my own re-estimate. `code/06c` keeps the with-SIVB run (`regression_with_failed.csv`, n = 12), and `specs_tried.md` #6–#7 log both |
| A2 · Normal p-values and HC1 | fixed | Commit `6459083`. `outputs/regression_main.txt` reports `Covariance Type: HC3` and t-statistics, with 7 residual df. My own HC3 with t₇ p-values: log assets p = 0.0232 (yours 0.0232) |
| A3 · Proposal hypothesis; "today" screen on 2022 data | unaddressed | Half of this is done. **Screen: fixed** (commit `9932a41`). `code/02 2026Q3` rebuilds `outputs/bhc_measures_2026Q3.csv` (10 holding companies) identically, and the dashboard's screen tab opens on "Today: latest call reports (09/30/2026)". **Hypothesis: unaddressed**, as your response says. `PROPOSAL.md:14` gained one sentence (commit `2601c58`), but the "TEAM HYPOTHESIS AND THOUGHTS" section (`PROPOSAL.md:23–25`) is still motivation, not a hypothesis you can test |
| A4 · Download not scripted; versions not pinned | fixed | Commits `2b21ebe`, `cda991b`. `code/00_download_call_reports.py 2022Q4 12/31/2022` exited 0 in 1.9 s, and `2026Q3 09/30/2026` in 1.3 s. `requirements.txt` pins all 79 packages, and the venv built from it on Python 3.11.18 ran every step |

**3 of 4 fixed, 1 still open.**

## Checkpoint 3 checks

| Check | Result |
|---|---|
| Reruns from scratch (full sample) | ❌ full sample not built (B1). On the 12 v0 banks: ✅ every step except the CRSP pull, all CSVs identical |
| Inputs have provenance | ✅ `inputs/call_reports/README.md` pull log, plus a `download.provenance.txt` per quarter |
| Keys unique, merges validated | ✅ `bhc_rssd` asserted, and `validate=` on every merge. My own merge of your link table (`validate="m:1"`) gives the same 10 and 12 holding companies |
| No look-ahead / survivorship | ⚠️ 12/31/2022 is the right quarter, but 9 of your 12 holding companies resubmitted it after the event, and you use the current vintage (B3; disclosed) |
| LLM leakage handled | n/a |
| `specs_tried.md` complete | ✅ #1–#9 match the code and outputs |
| Magnitudes discussed | ⚠️ coefficients only, at N = 11 (B1) |
| Hand checks | ⚠️ measures (fake data, MDRM) and links (21/21) ✅. The CAR check is still the auditor's, not yours (B4) |
| Threats to validity | ✅ README §"Threats to validity", including amendments and the 2022 link table for 2026 |
| Every number traces to `outputs/` | ✅ the README example row, `specs_tried.md` #6–#8 and the response tables match the CSVs |
| Dashboard matches `outputs/` | ✅ on PR #9: "11 banks … R² = 0.68" (`regression_main.csv`: 0.6839); "SVB uninsured deposit share 94%" (`analysis_sample.csv`: 0.9388) |

Steps not rerun by design: the CRSP pull (`code/03`, `04`), which uses instructor-provided WRDS/CRSP data. I used your committed `outputs/car_0_2.csv`. This is not counted against you.

## Getting ready for Dec 1

Presentations run only from URLs, with a hard cutoff at 9 minutes (10:45 section) or 10 minutes (12:10 section). Put your URL(s) in column G of the Team Projects sheet.

| Check | Result |
|---|---|
| Dashboard launches from a clean clone | ✅ `streamlit run app.py --server.headless true --server.port 8599` on a clean export of `61ed6c7`: `/_stcore/health` returned `ok` after 2 s. A headless browser clicked all 4 tabs, with no exceptions on the page or in the log |
| Dashboard shows the v1 numbers from `outputs/` | ⚠️ it reads only `outputs/` (`app.py:20-22`), and the numbers match. But they are v0 numbers, and the deployed app is built from `main`, which still has the CP2 regression (N = 12 with SIVB, HC1; `app.py:87` on `main` says "HC1") (B2) |
| README links the live URL(s) | ✅ `README.md:5` links https://team-helble-final.streamlit.app/ (the live site itself wasn't checked). `requirements.txt` was tested on Python 3.11: set the same version in the Streamlit Cloud app settings |

**Core story for 9–10 minutes:** the question; the two measures; the full-sample regression without failed banks, with the scatter; then the "today" screen. The ZION and with-SIVB robustness rows, and the amendments result, can each be one sentence.

## What holds up

- **Exact reproduction, now including the download.** Your `code/00` fetched both quarters from FFIEC in under 2 seconds each. Then `02` (FAKE, 2022Q4, 2026Q3), `05`, `06`, `06b` and `06c` reproduced every CSV in `outputs/`: `bank_measures_2022Q4` (4,756 × 20), `bank_measures_2026Q3` (4,267 × 20), `bhc_measures_2022Q4` (12), `bhc_measures_2026Q3` (10), `analysis_sample` (12 × 30), and the three regressions (max relative difference 3e-14). The `.txt` files differ only in the date and time lines.
- **Independent recomputation.** My own parser of the raw FFIEC files (RCFD-then-RCON, summed over your link table) gives the same `uninsured_dep_share` and `unreal_loss_to_adj_equity` for all 10 holding companies in 2026Q3 and all 12 in 2022Q4 (max difference 1.1e-16; e.g. JPM 2026Q3 0.6287 and 0.1128). My own OLS with HC3 and t₇ p-values gives your main regression: uninsured −0.1528 (SE 1.0837, p 0.892), loss ratio +0.0849 (SE 0.7520, p 0.913).
- **Rules written before running.** `DECISIONS.md` fixes the failed-bank rule (in-window failures out, FRC kept) before the regression. `specs_tried.md` logs #6–#9 with what each run replaced.
- **The amendments check.** `dev/check_amendments.py` turns your self-audit's finding 10 into numbers. 9 of 12 holding companies, and 41% of filers with assets ≥ $1B, resubmitted 12/31/2022 after Mar 9, 2023 (`audits/amendments_check_summary.csv`). You found this yourselves. B3 is about testing it.
- **The "today" screen handles banks that no longer exist.** SIVB and CMA (merged into FITB) are named on screen rather than silently dropped.

## New findings

### B1 · Blocking · v1 is not on the full sample

**Evidence:** `outputs/analysis_sample.csv` has 12 rows (11 in the regression). `README.md:20` says "Sample (v0): 12 banks … The v1 target is all listed U.S. banks (about 100)". The dashboard header reads "v0 (12 banks)". `audits/04_audit_response.md`, "Not yet done for v1": "The full-sample run (about 100 banks) is not in the repo yet."

**Why it matters:** Checkpoint 3 was v1 on the full sample. At N = 11 with 4 coefficients, as your own dashboard says, "this is a pipeline check, not evidence." The research question can't be answered yet.

**Fix:** Run the v1 plan (`docs/internal/v1_plan_nov17_to_nov21.md`): build the universe from the NY Fed link file, apply the pre-logged size and liquidity filters, pull CRSP for all of them, and rerun `05`–`06c`. Report the link match rate and a hand-checked sample of links (README threat on link quality). Add each filter and the final N to `specs_tried.md`.

**How to show it's fixed:** `analysis_sample.csv` has the full sample, with every exclusion counted. I will rerun `02`, `05`, `06`, `06b` and `06c` from the scripted download and your committed `car_0_2.csv`.

### B2 · Major · The live dashboard deploys from `main`, and the work since CP2 isn't on `main`

**Evidence:** `README.md:5` and STATUS row 5 say the app is deployed from `main`. `main` (`4cceb8a`) has only the CP2 audit merged since Checkpoint 2. Its `outputs/regression_main.csv` is the 12-bank regression with SIVB (`n_obs` = 12, no `cov_type` column), and its `app.py:87` says "Heteroskedasticity-robust (HC1) standard errors." The A1–A4 fixes, the 2026Q3 screen and the response file exist only on PR #9.

**Why it matters:** Presentations run from the URL. As things stand, the live app would show the specification your own response retires.

**Fix:** Merge PR #9 (and PR #6, as your response plans), then reload the deployed app and check the Analysis tab says 11 banks and HC3.

**How to show it's fixed:** `main` contains `61ed6c7` or its successor.

### B3 · Major · The 12/31/2022 call reports you use include resubmissions made after the event

**Evidence:** `audits/amendments_check.md` and `audits/amendments_check_summary.csv`: the main bank of 9 of 12 holding companies last updated its 12/31/2022 report after Mar 9, 2023, all after the FDIC's Jul 24, 2023 letter. So did 407 of 986 filers with assets ≥ $1B. The bulk file's own `Readme.txt` (downloaded 2026-11-22) says it holds reports "processed by the FFIEC Central Data Repository (CDR) as of 2026-09-15", and `inputs/call_reports/README.md:30-31` logs the same vintage. So your measures include every resubmission up to then. The README threats list discloses this.

**Why it matters:** This is seed 6's call-report-date item. Investors on Mar 9–13, 2023 saw the reports as originally filed. If resubmissions mostly revised uninsured deposits (the FDIC letter's subject), your main regressor is measured with information from after the event. In v1, about 41% of the sample is affected.

**Fix:** Carry a `resubmitted_after_event` flag into `analysis_sample.csv`. Add a logged robustness row without those banks, and one with an as-filed uninsured measure where you can get it (FR Y-9C, or the banks' 10-K/10-Q for Q4 2022). Then say in the README whether the main coefficients move.

**How to show it's fixed:** The flag column exists, and `specs_tried.md` has the robustness row and its output file.

### B4 · Minor · The CAR step's hand check is still the auditor's

**Evidence:** `audits/04_audit_response.md` ("Also from the audit") cites the auditor's CP2 yfinance check as the CAR hand check. The team's own recomputation, "a spreadsheet recomputation of KEY from CRSP", is "still planned (v1 plan, task 9)".

**Why it matters:** Checklist item 8 asks the team to recompute one number per pipeline step. In v1 the event study runs on ~100 banks, many of them small and illiquid, where a CRSP spreadsheet check is most informative.

**Fix:** Do the KEY check (and one small bank in v1). Record the inputs, the formula and both values in `audits/`.

**How to show it's fixed:** A committed hand-check file whose number matches `car_0_2.csv` to 4 decimals.

## How to respond

This audit is `audits/05_instructor_audit.md` in your repo. Fix what you can, then add `audits/06_audit_response.md`, replying to each **B** finding and to each CP2 finding still open (A3): fixed (the commit), disputed (why), or disclosed as a limitation (where).

There's no separate deadline for this response. Keep working through these until your final deliverables are due: the final repo is audited again then.
