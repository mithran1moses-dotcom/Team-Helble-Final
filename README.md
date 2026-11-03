# Bank Fragility: SVB, and Who's Next

**Team Helble** · Final project (Seed 6)

> **Dashboard:** _link TBD_ · **Dashboard repo:** _link TBD_

## Question

When Silicon Valley Bank failed (March 10, 2023), did listed banks with more **uninsured deposits** and larger **unrealized securities losses** suffer worse stock returns? Using the same measures, which listed banks look most fragile **today**?

**Who'd pay:** bank regulators (supervisory screening) and bank investors (risk screening).
**Benchmark paper:** Jiang, Matvos, Piskorski & Seru (2023), *Monetary Tightening and U.S. Bank Fragility in 2023: Mark-to-Market Losses and Uninsured Depositor Runs?*

## The final dataset (read backwards)

**Unit of observation:** one listed bank holding company (BHC) for one event.
**Key:** `rssd_id` (the BHC's Federal Reserve ID), which must be unique (`assert`).
**Sample:** listed U.S. banks with Q4 2022 call report data and enough return history. Target is about 100 banks for the MVP.

| rssd_id | ticker | bank_name | report_period | total_assets | total_equity | uninsured_dep_share | unreal_loss_to_equity | htm_loss | afs_loss | car_0_5 | mkt_cap | avg_dollar_vol |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| _id_ | ZION | Zions Bancorp | 12312022 | _$K_ | _$K_ | _0.xx_ | _0.xx_ | _$K_ | _$K_ | _−0.xx_ | _$_ | _$_ |

_(Placeholder row. Replace it with a real row from `outputs/` once the proof of concept runs.)_

| Variable | Definition | Source |
|---|---|---|
| `uninsured_dep_share` | RCON5597 / RCON2200 | Call report RC-O Memo 2, RC |
| `unreal_loss_to_equity` | [(1754−1771) + (1772−1773)] / 3210 | Call report RC-B, RC |
| `htm_loss`, `afs_loss` | Amortized cost minus fair value (positive = loss) | RC-B |
| `car_0_5` | Cumulative abnormal return, days 0 to +5, where day 0 = Mar 9, 2023. Market model vs. SPY, estimation window ending before 2023. | yfinance |
| `mkt_cap`, `avg_dollar_vol` | Pre-event size and liquidity filters | yfinance |

**Timing rule:** bank characteristics come from the **12/31/2022** call report, the last one filed before the event, so there is no look-ahead.

**Planned regression:**
`CAR_i = a + b1·uninsured_dep_share + b2·unreal_loss_to_equity + b3·log(total_assets) [+ b4·interaction] + e`, with robust standard errors.

**Chart sketch:** a scatter of `unreal_loss_to_equity` (x) against `car_0_5` (y). Dot size shows `uninsured_dep_share`, and SVB-like banks are labeled.

## Repo layout

```
code/                       numbered pipeline steps (run in order)
  02_build_bank_measures.py   call report bulk files → one row per bank
inputs/
  call_reports/               raw FFIEC bulk files (git-ignored; see README there for provenance)
  links/                      RSSD ↔ ticker links (hand map committed; raw NY Fed file git-ignored)
temp/                       intermediate files (git-ignored, rebuilt)
outputs/                    final datasets, tables, figures (every reported number comes from here)
audits/                     self-audits per checkpoint
dev/                        scratch work and test helpers (not part of the pipeline)
```

## How to run

```bash
pip install -r requirements.txt
# 1. Download the Q4 2022 call reports (see inputs/call_reports/README.md)
python code/02_build_bank_measures.py 2022Q4 12312022
```

To test without real data:
```bash
python dev/make_fake_call_reports.py
python code/02_build_bank_measures.py FAKE 12312022
```

## Threats to validity (living list)

- **Survivorship:** the most fragile banks (SIVB, SBNY, FRC, PACW) failed or merged, and yfinance may not have their returns.
- **Entity mismatch:** the stock belongs to the holding company, but call reports are filed by the bank subsidiaries.
- **RSSD → ticker link quality:** we will report the match rate and hand-check a sample.
- **Uninsured deposits (RCON5597)** are reported only by banks with at least $1B in assets.
- **Illiquid small banks:** their returns are noisy, so we apply size and liquidity filters (logged in `specs_tried.md`).
- **Day 0:** Mar 9 (SVB's stock crashed) vs. Mar 10 (SVB closed). We will show both.
