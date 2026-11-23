"""
05b_asfiled_uninsured.py

Compares each holding company's uninsured deposits in our call-report data (the
current version, often resubmitted after the event) with the figure in its 2022
10-K (filed Feb 2023, before the event), and builds an as-filed uninsured share
for the robustness regression in code/06e (instructor audit B3).

Inputs : outputs/analysis_sample.csv                 (code/05)
         inputs/asfiled/uninsured_10k_2022q4.csv     (hand-collected; see the README there)
Output : outputs/asfiled_uninsured_comparison.csv    one row per holding company

uninsured_dep_share_asfiled, the share the market could have seen:
    - not resubmitted after the event: the call-report share (already as filed)
    - resubmitted, and the 10-K figure has call-report scope: 10-K uninsured / call-report deposits
    - resubmitted, and the 10-K figure has a different scope (JPM, BAC, USB): missing
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# 1. Our sample and the hand-collected 10-K figures, one row each per ticker.
sample = pd.read_csv(OUT / "analysis_sample.csv")
tenk = pd.read_csv(ROOT / "inputs" / "asfiled" / "uninsured_10k_2022q4.csv")
assert tenk["ticker"].is_unique and set(tenk["ticker"]) == set(sample["ticker"])
df = sample[["ticker", "resubmitted_after_event", "uninsured_deposits", "total_deposits",
             "uninsured_dep_share"]].merge(
    tenk[["ticker", "filing_date", "uninsured_bn_10k", "comparable_to_call_report"]],
    on="ticker", how="left", validate="1:1")

# 2. Compare in $ billions (call-report amounts are in $ thousands).
#    pct_diff > 0: the current call report is higher than what the 10-K reported.
df["uninsured_bn_call_report"] = df["uninsured_deposits"] / 1e6
df["pct_diff"] = df["uninsured_bn_call_report"] / df["uninsured_bn_10k"] - 1

# 3. The 10-Ks were all filed before day 0, so they are numbers the market saw.
assert (pd.to_datetime(df["filing_date"]) < pd.Timestamp("2023-03-09")).all()

# 4. The as-filed share (rules in the docstring).
asfiled_from_10k = df["uninsured_bn_10k"] * 1e6 / df["total_deposits"]
df["uninsured_dep_share_asfiled"] = df["uninsured_dep_share"].where(~df["resubmitted_after_event"])
use_10k = df["resubmitted_after_event"] & df["comparable_to_call_report"]
df.loc[use_10k, "uninsured_dep_share_asfiled"] = asfiled_from_10k[use_10k]

# 5. Check: where a comparable 10-K exists for a bank that did NOT resubmit
#    (CMA, SIVB), it should match the call report. If not, the 10-K is a poor stand-in.
check = df[~df["resubmitted_after_event"] & df["comparable_to_call_report"]]
assert (check["pct_diff"].abs() < 0.01).all(), check[["ticker", "pct_diff"]]

df = df.drop(columns=["uninsured_deposits", "total_deposits"])
df.to_csv(OUT / "asfiled_uninsured_comparison.csv", index=False)
print(df.round(3).to_string(index=False))
print("Wrote outputs/asfiled_uninsured_comparison.csv")
