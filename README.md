# Bank Fragility: SVB, and Who's Next

**Team Helble** · Final project (Seed 6)

> **Dashboard (live):** https://team-helble-final.streamlit.app/ · built from `app.py` (reads only `outputs/`), deployed from this repo's `main` branch, so it updates after each merge · run locally with `streamlit run app.py`

## Question

When Silicon Valley Bank failed (March 10, 2023), did listed banks with more **uninsured deposits** and larger **unrealized securities losses** suffer worse stock returns? Using the same measures, which listed banks look most fragile **today**?

**Who'd pay:** bank regulators (supervisory screening) and bank investors (risk screening).
**Benchmark paper:** Jiang, Matvos, Piskorski & Seru (2023), *Monetary Tightening and U.S. Bank Fragility in 2023: Mark-to-Market Losses and Uninsured Depositor Runs?*

## The final dataset (read backwards)

_Team decisions are logged in [`DECISIONS.md`](DECISIONS.md), which overrides this README wherever they conflict._

**Unit of observation:** one listed bank holding company (BHC) for one event. Call reports are filed by the bank subsidiaries, so we **sum each BHC's subsidiaries' dollar amounts first, then compute ratios**.
**Key:** `bhc_rssd` (the BHC's Federal Reserve ID), which must be unique (`assert`). Subsidiary-level files use `bank_rssd`.
**Sample (v0):** 12 banks: JPM, BAC, WFC, USB, PNC, TFC, FITB, KEY, ZION, WAL, CMA, SIVB. The v1 target is all listed U.S. banks (about 100) with Q4 2022 call report data and enough return history.

| bhc_rssd | ticker | bhc_name | report_period | total_assets | total_equity | uninsured_dep_share | htm_loss | afs_loss | unreal_loss_to_adj_equity | htm_loss_to_equity | car_0_2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 276579 | ZION | ZIONS BANCORPORATION, NATIONAL ASSOCIATION | 12312022 | 89,544,919 | 4,893,499 | 0.498 | −113,126 | 1,623,190 | 0.232 | −0.023 | −0.358 |

_(Real row from `outputs/analysis_sample.csv`, rebuilt 2026-11-09. Dollar amounts in $ thousands. ZION's HTM loss is negative: see the AFS-to-HTM transfer item in `audits/01_self_audit.md`.)_

| Variable | Definition | Source |
|---|---|---|
| `uninsured_dep_share` | RCON5597 / RCON2200 (summed over the BHC's subsidiaries) | Call report RC-O Memo 2, RC |
| `htm_loss`, `afs_loss` | Amortized cost minus fair value (positive = loss): HTM = 1754 − 1771, AFS = 1772 − 1773 | RC-B |
| `unreal_loss_to_adj_equity` | **Main measure.** (HTM loss + AFS loss) / (total equity + AFS loss). AFS losses are added back to the denominator because they are already deducted from book equity (3210). Follows Jiang, Matvos, Piskorski & Seru (2023). | RC-B, RC |
| `htm_loss_to_equity` | **Robustness.** HTM loss / total equity (3210) | RC-B, RC |
| `car_0_2` | Cumulative abnormal return over trading days 0 to +2 (Mar 9, 10 and 13, 2023), where day 0 = Mar 9, 2023. Market model vs. SPY, estimation window ending before 2023. SIVB: day 0 only. | CRSP daily stock file via WRDS (`ret`, includes dividends; delisting returns where they apply) |
| `mkt_cap`, `avg_dollar_vol` | Pre-event size and liquidity filters. **v1 only** (not needed for the 12 large v0 banks). | CRSP via WRDS (`prc`, `shrout`, `vol`) |

**Why days 0 to +2:** the window covers SVB's stock crash (Mar 9), its seizure (Mar 10), and the Signature Bank closure and federal backstop (announced Sunday Mar 12, first traded Mar 13). It stops before the Credit Suisse shock on Mar 15. A longer window (e.g. 0 to +4) can be a robustness check, logged in `specs_tried.md`.

**Timing rule:** bank characteristics come from the **12/31/2022** call report, the last one filed before the event. **Caveat:** we use the current version of that report, and for 9 of our 12 holding companies the main bank resubmitted it after Mar 9, 2023 (`audits/amendments_check.md`), so some values may differ from what the market saw.

**Planned regression:**
`car_0_2_i = a + b1·uninsured_dep_share + b2·unreal_loss_to_adj_equity + b3·log(total_assets) [+ b4·interaction] + e`, with HC3 robust standard errors and t-based p-values. Banks that failed inside the event window (SIVB in v0) are left out of the main spec and reported in a robustness run.

**Chart sketch:** a scatter of `unreal_loss_to_adj_equity` (x) against `car_0_2` (y). Dot size shows `uninsured_dep_share`, and SVB-like banks are labeled.

## Repo layout

```
DECISIONS.md                team decisions (source of truth)
CLAUDE.md                   instructions for coding agents
STATUS.md                   where the project stands
PROPOSAL.md                 project proposal (HW8); images in images/
specs_tried.md              log of every regression spec run
run_all.py                  rebuilds every output in order (python run_all.py)
code/                       numbered pipeline steps (run in order)
  00_download_call_reports.py FFIEC call reports for one quarter → inputs/call_reports/<quarter>/ (git-ignored)
  01a_download_nyfed_link.py  NY Fed CRSP-FRB link file → inputs/links/raw/
  01b_build_link_table.py     ticker → holding company → bank subsidiaries (inputs/links/bank_link_v0.csv)
  02_build_bank_measures.py   call report bulk files → outputs/bank_measures_*.csv (per bank), outputs/bhc_measures_*.csv (per holding company)
  03_download_crsp.py         CRSP daily returns via WRDS, 12 banks + SPY, matched by PERMNO → inputs/prices/crsp/ (git-ignored; needs WRDS login)
  04_event_study.py           market model vs SPY (CRSP returns) → outputs/car_0_2.csv
  05_build_analysis_sample.py link + measures + CARs → outputs/analysis_sample.csv (12 rows)
  06_regression.py            regression, failed banks out (HC3, t p-values) → outputs/regression_main.*, scatter → outputs/figures/
  06b_robustness_drop_zion.py    main spec without ZION → outputs/regression_drop_zion.*
  06c_robustness_with_failed.py  main spec with SIVB put back in → outputs/regression_with_failed.*
  06d_robustness_not_resubmitted.py  main spec on reports not resubmitted after the event → outputs/regression_not_resubmitted.*
inputs/
  call_reports/               raw FFIEC bulk files (git-ignored; see README there for provenance)
  links/                      RSSD ↔ ticker links (hand map committed; raw NY Fed file git-ignored)
  prices/crsp/                CRSP returns from WRDS (git-ignored, WRDS license; README and provenance note committed)
temp/                       intermediate files (git-ignored, rebuilt)
outputs/                    final datasets, tables, figures (every reported number comes from here)
audits/                     self-audits per checkpoint, plus standalone checks (e.g. mdrm_check.md)
app.py                      Streamlit dashboard: Introduction, Methodology, Analysis, Interactive fragility screen
dev/                        scratch work, test helpers, and the retired yfinance script with its old price snapshot (not part of the pipeline)
images/                     pictures used by PROPOSAL.md (dashboard mockup)
docs/                       reference only: course instructions (docs/course/) and internal planning notes (docs/internal/)
```

## How to run

Use Python 3.11 in a fresh virtual environment. `requirements.txt` pins every package to the exact version we tested.

```bash
python3.11 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

1. Download the inputs. The call reports are scripted: `python code/00_download_call_reports.py 2022Q4 12/31/2022`, and `2026Q3 09/30/2026` for the latest quarter (`inputs/call_reports/README.md`). The FFIEC NIC files are still manual (`inputs/links/README.md`).
2. Pull the CRSP returns. **This needs a WRDS login** (the script asks for your username and password and stores nothing; approve the Duo push). See `inputs/prices/crsp/README.md`.

```bash
python code/03_download_crsp.py
```
3. Rebuild every output, fake-data test first:

```bash
python run_all.py
```

Add `--download` to re-fetch the NY Fed link file and the CRSP returns (asks for your WRDS login) and rebuild the link table first.

4. Open the dashboard:

```bash
streamlit run app.py
```

To test the measures code alone without real data:
```bash
python dev/make_fake_call_reports.py
python code/02_build_bank_measures.py FAKE 12312022
python dev/check_fake_bhc_measures.py   # compares to hand-computed answers
```

## Threats to validity (living list)

- **Survivorship:** the most fragile banks (SIVB, SBNY, FRC, PACW) failed or merged. Yahoo has no data for SIVB or CMA (Comerica, acquired by Fifth Third), which is why all returns now come from CRSP, which keeps delisted stocks.
- **One return source:** all 12 banks and SPY use CRSP `ret` via WRDS (matched by PERMNO, not ticker). Rebuilding needs a WRDS login; the raw data cannot be shared.
- **CAR is a sum of simple daily abnormal returns.** For very large moves (WAL fell about 64% over the window) the sum is more negative than the compounded loss; a buy-and-hold abnormal return is a possible robustness check.
- **SIVB stopped trading after Mar 9, 2023** (halted Mar 10, then seized), so its `car_0_2` covers only day 0 (Mar 9). CRSP lists a Mar 10 return for SIVB, but it is a bid/ask quote with no trade (negative price), so `code/04_event_study.py` drops it, along with any other no-trade day. SIVB's CAR is not comparable to the other banks' three-day CARs; the `note` column in `outputs/car_0_2.csv` flags it.
- **Failed banks are the shock, not a response to it.** SIVB (and SBNY in v1) failed inside the event window, and SIVB's CAR covers day 0 only, so they are flagged `failed_in_window` in `outputs/analysis_sample.csv` and left out of the main regression (instructor audit A1). With N = 12 SIVB alone flipped the sign of the loss-ratio slope; the with-SIVB run is kept in `outputs/regression_with_failed.csv`.
- **"Today" screen uses the 12/31/2022 link table.** The dashboard's latest-quarter view (09/30/2026, `outputs/bhc_measures_2026Q3.csv`) sums the same bank subsidiaries as in 2022. SIVB (failed) and CMA (merged into FITB, Feb 2026) no longer have a filing bank and are dropped; FITB's numbers include Comerica's. Subsidiaries a holding company added after 2022 are not captured; that needs NIC relationships as of 2026.
- **Call reports resubmitted after the event (look-ahead):** the FFIEC bulk file holds the latest version of each 12/31/2022 report. 9 of our 12 holding companies (all but SIVB, CMA, WFC) have a main bank that resubmitted after Mar 9, 2023, all after the FDIC's Jul 24, 2023 letter on uninsured deposits; so did 41% of all filers with assets ≥ $1B. The file shows when, not what changed. They are flagged `resubmitted_after_event` in `outputs/analysis_sample.csv`, and `code/06d` reruns the main spec without them: not estimable at v0 (2 banks left), runs in v1 (`audits/amendments_check.md`).
- **Entity mismatch:** the stock belongs to the holding company, but call reports are filed by the bank subsidiaries. We sum subsidiaries to the holding company using the link table.
- **RSSD → ticker link quality:** 12 of 12 tickers matched to the NY Fed file, and all 21 link-table rows hand-checked (NIC, or FDIC 12/31/2022 records for banks that have since closed): `audits/link_check_sheet.md`. In v1 (about 100 banks) we will report the match rate and hand-check a sample.
- **Uninsured deposits (RCON5597)** are reported only by banks with at least $1B in assets.
- **AFS-to-HTM transfers:** losses locked in when a bank moved securities from AFS to HTM sit in equity (AOCI), not in HTM cost minus fair value, so the loss ratio understates fragility for those banks (Zions shows a negative HTM loss). Kept as a limitation; robustness check without ZION in `outputs/regression_drop_zion.csv` (`specs_tried.md` #5).
- **Illiquid small banks:** their returns are noisy, so we apply size and liquidity filters (logged in `specs_tried.md`). Matters for v1, not the 12 large v0 banks.
- **Day 0:** decided as Mar 9 (SVB's stock crashed). Mar 10 (SVB closed) is a possible robustness check.
- **Convenience sample:** the 12 v0 banks were chosen knowing the outcome; v1 uses all listed banks.
