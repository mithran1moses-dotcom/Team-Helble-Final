# Bank Fragility: SVB, and Who's Next

**Team Helble** · Final project (Seed 6)

> **Dashboard:** run locally with `streamlit run app.py` (reads only `outputs/`) · hosted link TBD

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
| _id_ | ZION | Zions Bancorporation | 12312022 | _$K_ | _$K_ | _0.xx_ | _$K_ | _$K_ | _0.xx_ | _0.xx_ | _−0.xx_ |

_(Placeholder row. Replace it with a real row from `outputs/` once the proof of concept runs.)_

| Variable | Definition | Source |
|---|---|---|
| `uninsured_dep_share` | RCON5597 / RCON2200 (summed over the BHC's subsidiaries) | Call report RC-O Memo 2, RC |
| `htm_loss`, `afs_loss` | Amortized cost minus fair value (positive = loss): HTM = 1754 − 1771, AFS = 1772 − 1773 | RC-B |
| `unreal_loss_to_adj_equity` | **Main measure.** (HTM loss + AFS loss) / (total equity + AFS loss). AFS losses are added back to the denominator because they are already deducted from book equity (3210). Follows Jiang, Matvos, Piskorski & Seru (2023). | RC-B, RC |
| `htm_loss_to_equity` | **Robustness.** HTM loss / total equity (3210) | RC-B, RC |
| `car_0_2` | Cumulative abnormal return over trading days 0 to +2 (Mar 9, 10 and 13, 2023), where day 0 = Mar 9, 2023. Market model vs. SPY, estimation window ending before 2023. | yfinance |
| `mkt_cap`, `avg_dollar_vol` | Pre-event size and liquidity filters. **v1 only** (not needed for the 12 large v0 banks). | yfinance |

**Why days 0 to +2:** the window covers SVB's stock crash (Mar 9), its seizure (Mar 10), and the Signature Bank closure and federal backstop (announced Sunday Mar 12, first traded Mar 13). It stops before the Credit Suisse shock on Mar 15. A longer window (e.g. 0 to +4) can be a robustness check, logged in `specs_tried.md`.

**Timing rule:** bank characteristics come from the **12/31/2022** call report, the last one filed before the event, so there is no look-ahead.

**Planned regression:**
`car_0_2_i = a + b1·uninsured_dep_share + b2·unreal_loss_to_adj_equity + b3·log(total_assets) [+ b4·interaction] + e`, with robust standard errors.

**Chart sketch:** a scatter of `unreal_loss_to_adj_equity` (x) against `car_0_2` (y). Dot size shows `uninsured_dep_share`, and SVB-like banks are labeled.

## Repo layout

```
DECISIONS.md                team decisions (source of truth)
CLAUDE.md                   instructions for coding agents
STATUS.md                   where the project stands
specs_tried.md              log of every regression spec run
run_all.py                  rebuilds every output in order (python run_all.py)
code/                       numbered pipeline steps (run in order)
  01a_download_nyfed_link.py  NY Fed CRSP-FRB link file → inputs/links/raw/
  01b_build_link_table.py     ticker → holding company → bank subsidiaries (inputs/links/bank_link_v0.csv)
  02_build_bank_measures.py   call report bulk files → outputs/bank_measures_*.csv (per bank), outputs/bhc_measures_*.csv (per holding company)
  03_download_prices.py       yfinance prices, 12 banks + SPY → inputs/prices/yfinance_prices.csv (committed snapshot)
  04_event_study.py           market model vs SPY → outputs/car_0_2.csv
  05_build_analysis_sample.py link + measures + CARs → outputs/analysis_sample.csv (12 rows)
  06_regression.py            regression (HC1) → outputs/regression_main.*, scatter → outputs/figures/
inputs/
  call_reports/               raw FFIEC bulk files (git-ignored; see README there for provenance)
  links/                      RSSD ↔ ticker links (hand map committed; raw NY Fed file git-ignored)
  prices/                     yfinance snapshot; crsp/ holds CRSP returns for delisted banks (git-ignored, WRDS license)
temp/                       intermediate files (git-ignored, rebuilt)
outputs/                    final datasets, tables, figures (every reported number comes from here)
audits/                     self-audits per checkpoint
app.py                      Streamlit dashboard: Introduction, Methodology, Analysis, Interactive fragility screen
dev/                        scratch work and test helpers (not part of the pipeline)
```

## How to run

```bash
pip install -r requirements.txt
```

1. Download the manual inputs: the 12/31/2022 call reports (`inputs/call_reports/README.md`), the FFIEC NIC files (`inputs/links/README.md`) and, when available, CRSP returns for SIVB and CMA (`inputs/prices/crsp/README.md`).
2. Rebuild every output, fake-data test first:

```bash
python run_all.py
```

Add `--download` to re-fetch the NY Fed link file and Yahoo prices and rebuild the link table first (this overwrites the committed price snapshot).

3. Open the dashboard:

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

- **Survivorship:** the most fragile banks (SIVB, SBNY, FRC, PACW) failed or merged. yfinance has **no** data for SIVB or CMA (Comerica, acquired by Fifth Third), so their returns must come from CRSP (`inputs/prices/crsp/README.md`).
- **Mixed return sources:** 10 banks use Yahoo adjusted closes, delisted banks use CRSP `RET`. Both include dividends; small differences are possible.
- **CAR is a sum of simple daily abnormal returns.** For very large moves (WAL fell about 64% over the window) the sum is more negative than the compounded loss; a buy-and-hold abnormal return is a possible robustness check.
- **SIVB stopped trading after Mar 9, 2023** (halted Mar 10, then seized), so its `car_0_2` covers only day 0 (Mar 9). CRSP lists a Mar 10 return for SIVB, but it is a bid/ask quote with no trade (negative price), so `code/04_event_study.py` drops it, along with any other no-trade day. SIVB's CAR is not comparable to the other banks' three-day CARs; the `note` column in `outputs/car_0_2.csv` flags it.
- **Entity mismatch:** the stock belongs to the holding company, but call reports are filed by the bank subsidiaries. We sum subsidiaries to the holding company using the link table.
- **RSSD → ticker link quality:** we will report the match rate and hand-check a sample.
- **Uninsured deposits (RCON5597)** are reported only by banks with at least $1B in assets.
- **Illiquid small banks:** their returns are noisy, so we apply size and liquidity filters (logged in `specs_tried.md`). Matters for v1, not the 12 large v0 banks.
- **Day 0:** decided as Mar 9 (SVB's stock crashed). Mar 10 (SVB closed) is a possible robustness check.
- **Convenience sample:** the 12 v0 banks were chosen knowing the outcome; v1 uses all listed banks.
