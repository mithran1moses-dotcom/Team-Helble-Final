"""
Checks outputs/bhc_measures_FAKE.csv against answers worked out by hand from
the numbers in dev/make_fake_call_reports.py ($ thousands).

    python dev/make_fake_call_reports.py
    python code/02_build_bank_measures.py FAKE 12312022
    python dev/check_fake_bhc_measures.py

FAKEA = bank 1 + bank 2 (sum dollars first, then ratios):
    equity    250,000 + 15,000      = 265,000
    HTM loss  (400,000-360,000) + (90,000-75,000) = 40,000 + 15,000 = 55,000
    AFS loss  (300,000-280,000) + (30,000-27,000) = 20,000 +  3,000 = 23,000
    unreal_loss_to_adj_equity = (55,000 + 23,000) / (265,000 + 23,000) = 78,000 / 288,000
    htm_loss_to_equity        = 55,000 / 265,000
    uninsured_dep_share       = (900,000 + 150,000) / (2,000,000 + 170,000)
FAKEB = bank 3 only (bank 4 files no call report and is dropped):
    unreal_loss_to_adj_equity = (0 + 10) / (80 + 10)
    htm_loss_to_equity        = 0 / 80
    uninsured_dep_share       = missing (bank 3 is too small to report it)
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
bhc = pd.read_csv(ROOT / "outputs" / "bhc_measures_FAKE.csv").set_index("ticker")

# FAKEA: two banks summed.
a = bhc.loc["FAKEA"]
assert a["n_banks"] == 2
assert abs(a["unreal_loss_to_adj_equity"] - 78_000 / 288_000) < 1e-9
assert abs(a["htm_loss_to_equity"] - 55_000 / 265_000) < 1e-9
assert abs(a["uninsured_dep_share"] - 1_050_000 / 2_170_000) < 1e-9

# FAKEB: one filing bank; the non-filing bank was dropped.
b = bhc.loc["FAKEB"]
assert b["n_banks"] == 1
assert abs(b["unreal_loss_to_adj_equity"] - 10 / 90) < 1e-9
assert b["htm_loss_to_equity"] == 0
assert pd.isna(b["uninsured_dep_share"])

print("All fake-data checks passed.")
