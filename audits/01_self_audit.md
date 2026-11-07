# Self-audit 01 (v0 checkpoint)

Written 2026-11-07 by Mithran Moses with Claude Code, on branch `v0-pipeline`.
Covers the items listed in `DECISIONS.md` ("For the report / self-audit"), plus problems found while building v0.
Each answer points to the file that backs it up. **Status** is one of: OK, LIMITATION (known and documented), OPEN (must fix).

## 0. What v0 requires (DECISIONS.md)

| Requirement | Status | Where |
|---|---|---|
| Whole pipeline on a small sample | OK | `run_all.py` runs `code/02` → `06`; 12 banks |
| Dashboard skeleton | OK | `app.py` (4 tabs, reads only `outputs/`) |
| Self-audit | OK | this file |
| `specs_tried.md`, `STATUS.md`, `run_all.py` | OK | repo root |

## 1. Data and provenance

| Item | Status | Evidence |
|---|---|---|
| Call reports are from 12/31/2022, the last quarter before SVB failed (no look-ahead) | OK | `inputs/call_reports/README.md` pull log; `report_period` column in `outputs/bhc_measures_2022Q4.csv` |
| Every raw file has a source and download date | OK | pull logs in `inputs/call_reports/README.md`, `inputs/links/README.md`; `inputs/prices/yfinance_prices.provenance.txt` |
| Yahoo prices are a committed snapshot (Yahoo revises adjusted prices) | OK | `inputs/prices/yfinance_prices.csv` |
| MDRM codes (2170, 3210, 2200, 5597, 1754, 1771, 1772, 1773) checked against the FFIEC data dictionary for 12/31/2022 | **OPEN** | Not yet checked by a person. Spot check: SVB's HTM loss ($15.2B), BAC's ($108.6B) and WFC's ($41.6B) in `outputs/bank_measures_2022Q4.csv` match widely reported figures. |

## 2. Sample

| Item | Status | Evidence |
|---|---|---|
| **Convenience sample chosen knowing the outcome.** The 12 v0 banks were picked after the fact. v1 uses all listed banks. | LIMITATION | `inputs/links/v0_banks.csv`; README threats list |
| **Survivorship.** SIVB, SBNY, FRC, PACW failed or merged; Comerica (CMA) was acquired by Fifth Third. Yahoo has **no** data for SIVB or CMA. | **OPEN** | `inputs/prices/yfinance_prices.provenance.txt`; `outputs/car_0_2.csv` (blank CAR for both). Fix: CRSP export, steps in `inputs/prices/crsp/README.md`. |
| Exactly 12 holding companies, unique `bhc_rssd` | OK | asserted in `code/05_build_analysis_sample.py`; `outputs/analysis_sample.csv` |
| Regression uses 10 of 12 banks until CRSP arrives | LIMITATION | `banks_used` column in `outputs/regression_main.csv` |

## 3. Measures

| Item | Status | Evidence |
|---|---|---|
| **Loss-ratio choice and double counting.** Main = (HTM loss + AFS loss) / (total equity + AFS loss). AFS losses are already deducted from book equity, so they are added back to the denominator (Jiang, Matvos, Piskorski & Seru 2023). Robustness = HTM loss / equity. | OK | `add_ratios()` in `code/02_build_bank_measures.py` |
| **Holding company vs. subsidiary.** Dollar amounts are summed across each holding company's banks first, then ratios are computed. | OK | `aggregate_to_bhc()` in `code/02_build_bank_measures.py`; tested on fake data with hand-computed answers in `dev/check_fake_bhc_measures.py` |
| **Uninsured deposits (RCON5597) are only reported by banks with at least $1B in assets.** Small subsidiaries add deposits but no uninsured amount, which slightly understates the share. | LIMITATION | `n_banks_uninsured_reported` vs `n_banks` in `outputs/bhc_measures_2022Q4.csv` (affects JPM, CMA, WFC through tiny trust/limited-purpose banks) |
| **AFS-to-HTM transfers.** Losses on securities moved from AFS to HTM stay in equity (AOCI) and are left out of HTM cost minus fair value, so the loss ratio understates fragility for banks that transferred. Zions shows a negative HTM loss. | **OPEN** (team decision) | `htm_loss` for ZION in `outputs/bhc_measures_2022Q4.csv`; `STATUS.md` |

## 4. Event study

| Item | Status | Evidence |
|---|---|---|
| **Window choice justified against the news timeline.** Days 0 to +2 = Mar 9, 10, 13, 2023: SVB's crash, its seizure, and the Signature closure and backstop. Ends before the Credit Suisse shock on Mar 15. | OK | `DECISIONS.md`; README; `EVENT_DAYS` in `code/04_event_study.py` (asserted to be trading days) |
| Market model vs SPY, estimated on calendar 2022 only (ends before 2023) | OK | `code/04_event_study.py`; `n_est_days` = 250 in `outputs/car_0_2.csv` |
| **SIVB stopped trading Mar 10, so its CAR covers only day 0.** | OK (handled), LIMITATION (comparability) | `n_event_days` and `note` columns in `outputs/car_0_2.csv`; tested with a throwaway fake CRSP file |
| CAR is a sum of simple daily abnormal returns; for very large moves (WAL) it is more negative than the compounded loss | LIMITATION | README threats list; buy-and-hold CAR is a possible robustness check |
| Two return sources (Yahoo adjusted close; CRSP `RET` for delisted banks), both include dividends | LIMITATION | `return_source` column in `outputs/car_0_2.csv` |

## 5. Merges and keys

| Item | Status | Evidence |
|---|---|---|
| Every merge uses `validate=` and keys are asserted unique | OK | `code/01b`, `02`, `04`, `05` |
| **Link quality: match rate and hand-checked sample.** 12 of 12 tickers matched by name to the NY Fed file; 21 linked banks, of which 19 file call reports (the 2 trust companies without a call report are printed and dropped). Rows hand-checked: **0 of 21**. | **OPEN** | `inputs/links/bank_link_v0.csv` (`checked_by` blank); output of `code/02_build_bank_measures.py` |
| Two linked banks have no NIC record; identified from the call report filer list as Comerica Bank (60143) and MUFG Union Bank (212465, owned by USB 12/1/2022 to 5/26/2023) | OK, needs hand-check | `outputs/bank_measures_2022Q4.csv` |
| Zions is a bank with no holding company (`bhc_rssd` = `bank_rssd`) | OK | note on ZION row of `inputs/links/bank_link_v0.csv` |
| Banks owned by another bank are dropped to avoid double counting (consolidated in the parent's call report) | OK, needs hand-check | dropped list printed by `code/01b_build_link_table.py` |

## 6. Threats to validity

Kept as a living list in `README.md` ("Threats to validity"). Every item above marked LIMITATION is listed there.

## 7. Reproducibility

| Item | Status | Evidence |
|---|---|---|
| One command rebuilds every output from the inputs | OK | `python run_all.py`. On 2026-11-07 a full rerun reproduced every committed output byte for byte, except the clock time printed inside `outputs/regression_main.txt`. |
| Fake-data test runs before real data | OK | first steps of `run_all.py` |
| Manual downloads documented step by step | OK | READMEs in `inputs/call_reports/`, `inputs/links/`, `inputs/prices/crsp/` |
| Every number in the dashboard comes from `outputs/` and names its file | OK | `app.py` |
| Specs logged | OK | `specs_tried.md` (2 entries) |

## 8. Open issues (before the v0 deadline, Sat Nov 14)

1. **CRSP returns for SIVB and CMA.** Blocked on WRDS access. Then rerun `python run_all.py`.
2. **Hand-check all 21 link-table rows** and fill `checked_by`, `checked_on`.
3. **Verify MDRM codes** against the FFIEC data dictionary for 12/31/2022.
4. **Team decision on AFS-to-HTM transfer losses** (fix in v1, or document as a limitation).
5. Re-run the regression and update `specs_tried.md` once SIVB and CMA are in.
