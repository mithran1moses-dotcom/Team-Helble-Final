# Instructor audit: Team Helble, Checkpoint 2

**Repo:** mithran1moses-dotcom/Team-Helble-Final · **Audited commit:** `30aa41c` (2026-11-14, merge of PR #5 into `main`) · **Seed:** 6, bank fragility: SVB, and who's next

> Note from your human teacher: This review is generated with minimal supervision from Opus 5.5-high. It is thorough, but can be too generous at times and doesn't know my taste for what is "good". Grades it and I would assign are correlated, but noisy, ok? If you want additional feedback from _me_, you need to find me before/after/during class or during office hours for a guaranteed speedy reply. I will try to respond to emails and issues, but can not respond to student inquiries around the clock across the final weeks of class. Response times will be unpredictable, though during Thanksgiving week, I will do my best to respond quickly virtually, as in person options will be nil.

## Summary

This is careful v0 work that reproduces.
- I downloaded the 12/31/2022 FFIEC call reports myself and reran your pipeline from step 02. `bank_measures` (4,756 banks), `bhc_measures`, `analysis_sample` and both regressions came out identical.
- My own code, reading the raw FFIEC files, gives the same uninsured shares and loss ratios.
- A second return source (yfinance) gives the same CARs as your CRSP pull for the 10 banks Yahoo still has.
- Your self-audit already flags most of what matters.

The one thing to fix before v1: SIVB, the failing bank itself, sits in the regression with a one-day CAR. Without it, the two coefficients the project is about change materially (A1).

| Check | Result |
|---|---|
| Reruns from scratch | ✅ with the call reports downloaded (step 02 → 06b identical). The CRSP step needs WRDS and was not rerun; yfinance CARs match it (below) |
| Inputs have provenance | ✅ pull logs for call reports, NIC/NY Fed and CRSP |
| Keys unique, merges validated | ✅ `bhc_rssd` asserted, `validate=` everywhere |
| No look-ahead / survivorship | ✅ 12/31/2022 reports, 2022 estimation window, CRSP keeps SIVB and CMA. ⚠️ the sample was picked after the event (disclosed) |
| LLM leakage handled | n/a |
| `specs_tried.md` complete | ✅ 5 specs, matching the code |
| Magnitudes discussed | ⚠️ coefficients only (fine at v0) |
| Hand checks | ✅ measures (fake data, MDRM check), links (21/21). ⚠️ no CAR hand check yet: the auditor's yfinance check below can serve |
| Threats to validity | ✅ thorough README list |
| Every number traces to `outputs/` | ✅ README example row and `specs_tried.md` results match `outputs/` |

## What holds up

- **Full rerun on real data.** The FFIEC CDR bulk file "FFIEC CDR Call Bulk All Schedules 12312022.zip" (51 files) was downloaded 2026-11-15. With it, `code/02` (exit 0, 1.6 s), `05`, `06` and `06b` regenerate `bank_measures_2022Q4.csv` (4,756 × 20), `bhc_measures_2022Q4.csv` (12 × 20), `analysis_sample.csv`, `regression_main.csv` and `regression_drop_zion.csv`, all identical to the committed files.
- **Measures recomputed independently.** My own parser (RCFD-then-RCON for 3210, 1754, 1771, 1772, 1773; RCON2200 and 5597; summed over the subsidiaries in your link table, then divided) reproduces `uninsured_dep_share` and `unreal_loss_to_adj_equity` for all 12 holding companies. Largest difference 1.1e-16; e.g. SIVB 0.9388 and 0.9835. Your self-audit's finding 21 (numerator from reporting subsidiaries only) changes the share by less than 0.00005 for every bank.
- **CARs from a second source.** yfinance adjusted closes with a market model on 2022 vs SPY reproduce `car_0_2` to 4 decimals for all 10 banks still on Yahoo (e.g. WAL −0.7597, KEY −0.3347 vs −0.3348). Betas also match (e.g. ZION 1.1027 vs 1.1026). You can cite this as the CAR hand check your self-audit lists as open (finding 9).
- **Seed 6 items:**
  - **Call-report date:** the quarter before the event, filed by early Feb 2023.
  - **ID link quality:** NY Fed link plus NIC/FDIC hand checks on all 21 rows.
  - **Survivorship:** handled through CRSP by PERMNO.
  - **Small illiquid banks:** correctly deferred to v1.
- **Your PR #6 (`audits/02_external_findings.md`, Nov 16, after the audited commit, not yet merged).** It's useful work, and it engages with your own self-audit in the right way:
  - **Finding 10.** It turns your amended-reports finding from "plausible" into a dated, testable problem: the FDIC's July 24, 2023 guidance, and Q4 2022 restatements of uninsured deposits.
  - **CMA.** It explains that CMA's "delisting" is the February 2026 Fifth Third merger, not a 2023 failure. That bears on the "today" screen (A3).
  - **What I didn't check.** I haven't verified its external sources (not verified: the audit environment can't reach S&P Global, and I didn't check the others). My independent recomputation above used the same Nov 2026 bulk vintage you did, so it says nothing about the vintage question.
  - **Next steps.** Merge it, replace the trade-press links with the FDIC letter and Comerica's 8-K as you plan, and treat the bank-by-bank check (A4) as part of v1.

## Findings

### A1 · Major · SIVB is the event, but it is also an observation, with a one-day CAR, and it drives the slopes

**Evidence:**
- `outputs/car_0_2.csv`: SIVB has `n_event_days` = 1 (day 0 only); every other bank has 3.
- Its measures are the sample extremes (uninsured share 0.939, loss ratio 0.983; the next highest are 0.625 and 0.486).
- Re-estimating `06_regression.py`'s specification (auditor's own OLS, HC1) with and without it:

  | | All 12 | Without SIVB (11) |
  |---|---|---|
  | `uninsured_dep_share` | −0.442 (p = 0.26, t₈) | −0.153 (p = 0.81, t₇) |
  | `unreal_loss_to_adj_equity` | −0.048 (p = 0.87) | **+0.085** (p = 0.86) |
  | `log_total_assets` | +0.117 (p = 0.004) | +0.121 (p = 0.008) |

Your self-audit lists this as finding 8.

**Why it matters:** The question is whether other banks with SVB-like balance sheets fell more. SVB's own collapse is the shock, not a response to it, and its one-day CAR isn't comparable to the three-day CARs. With N = 12, it alone sets the sign of the loss-ratio slope.

**Fix:** In the main specification, exclude banks that failed during the event window (SIVB now; SBNY and FRC in v1 if they're in the universe). Report them separately, and keep the with-SIVB version as a logged robustness row in `specs_tried.md`.

**How to show it's fixed:** `regression_main.csv` excludes failed banks, and `specs_tried.md` has both rows.

### A2 · Minor · Small-sample inference uses normal p-values and HC1

**Evidence:** `06_regression.py:35` calls `.fit(cov_type="HC1")`. statsmodels then reports z-statistics with normal p-values. With 8 residual degrees of freedom, `log_total_assets` is p = 0.0001 (normal) vs 0.0044 (t₈). The intercept is p = 0.0001 vs 0.0038.

**Fix:** Use `fit(cov_type="HC3", use_t=True)` (HC3 behaves better at small N), and report t-based p-values. At v1 (~100 banks) this matters less, but the dashboard shows these p-values now.

**How to show it's fixed:** `regression_main.txt` shows t-statistics and the HC3 label.

### A3 · Minor · Proposal placeholder, and the "today" screen still shows 2022

**Evidence:** `PROPOSAL.md:23` still reads "TEAM HYPOTHESIS AND THOUGHTS" (your self-audit finding 3). The dashboard's "Interactive fragility screen" (`app.py:106-107`) filters the 12 v0 banks on 12/31/2022 measures, but the seed's second question is which banks look fragile **today**.

**Fix:** Fill in the hypothesis. For v1, run `02_build_bank_measures.py` on the latest quarter, which FFIEC already lists through 09/30/2026, and point the screen at it, labeled with its report date.

**How to show it's fixed:** The proposal has no placeholder, and the screen shows the latest report date.

### A4 · Minor · The call-report download can be scripted, and versions aren't pinned

**Evidence:**
- `inputs/call_reports/README.md` says the download is manual ("the site is a web form"). The auditor scripted it with `requests` in about 60 lines: the ASP.NET form fields are `ListBox1` (product), `DatesDropDownList`, `FormatType=TSVRadioButton` and `TabStrip1$Download_0`. It took seconds.
- `requirements.txt` has `pandas>=2.0` and bare `numpy`, `wrds`, `statsmodels`, `matplotlib`.

**Fix:** Add a `code/00_download_call_reports.py` so `run_all.py --download` covers it. Pin versions with `pip freeze`. Your self-audit's finding 10 (amended reports) is worth recording: the bulk file you used says "CDR data as of 2026-09-15", so it includes any later amendments.

**How to show it's fixed:** A fresh clone gets the call reports with one command.

## How to respond

This audit is `audits/03_instructor_audit.md` in your repo (`02` is your own external-findings file in PR #6). Fix what you can, then add `audits/04_audit_response.md`, replying to each finding ID: fixed (the commit), disputed (why), or disclosed as a limitation (where).

**Deadline: Saturday, November 21, 2026.**
