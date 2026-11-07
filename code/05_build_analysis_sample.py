"""
05_build_analysis_sample.py

Merges the three pieces into one analysis file, one row per bank holding company:
    link table      (who the 12 v0 holding companies are)   inputs/links/bank_link_v0.csv
    measures        (12/31/2022 call report ratios)          outputs/bhc_measures_2022Q4.csv
    event-study CAR (stock reaction, Mar 9-13, 2023)         outputs/car_0_2.csv

Output: outputs/analysis_sample.csv  (exactly 12 rows, unique bhc_rssd)
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# 1. The 12 holding companies, from the link table (one row per bank there,
#    so keep one row per holding company).
link = pd.read_csv(ROOT / "inputs" / "links" / "bank_link_v0.csv")
bhcs = link[["bhc_rssd", "ticker", "bhc_name"]].drop_duplicates()
assert bhcs["bhc_rssd"].is_unique and bhcs["ticker"].is_unique and len(bhcs) == 12

# 2. Add the call report measures. They were built from the same link table,
#    so every holding company must match, with the same ticker.
measures = pd.read_csv(OUT / "bhc_measures_2022Q4.csv").drop(columns=["bhc_name"])
sample = bhcs.merge(measures, on="bhc_rssd", how="left", validate="1:1", suffixes=("", "_measures"))
assert (sample["ticker"] == sample["ticker_measures"]).all()
sample = sample.drop(columns=["ticker_measures"])

# 3. Add the event-study results by ticker. Every ticker has a row in car_0_2.csv,
#    even when its CAR is missing (delisted banks waiting on CRSP).
car = pd.read_csv(OUT / "car_0_2.csv")
car = car.rename(columns={"note": "car_note", "source": "return_source"})
sample = sample.merge(car, on="ticker", how="left", validate="1:1")

# 4. Log of total assets, the size control in the regression ($ thousands as reported).
sample["log_total_assets"] = np.log(sample["total_assets"])

# 5. Checks required by the team: exactly 12 rows, one per holding company.
assert len(sample) == 12
assert sample["bhc_rssd"].is_unique

sample = sample.sort_values("ticker").reset_index(drop=True)
sample.to_csv(OUT / "analysis_sample.csv", index=False)
print(f"Wrote outputs/analysis_sample.csv: {len(sample)} rows, "
      f"{sample['car_0_2'].notna().sum()} with car_0_2")
print(sample[["ticker", "uninsured_dep_share", "unreal_loss_to_adj_equity",
              "log_total_assets", "car_0_2"]].round(3).to_string(index=False))
