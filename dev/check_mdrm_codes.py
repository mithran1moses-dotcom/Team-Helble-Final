"""
check_mdrm_codes.py: confirm that every call report field used in
code/02_build_bank_measures.py exists in the Federal Reserve's MDRM data
dictionary, with the expected name, on the forms our banks file, as of 12/31/2022.

    python dev/check_mdrm_codes.py

Source: Federal Reserve Micro Data Reference Manual (MDRM),
        https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip
The zip is downloaded into temp/ (git-ignored) and not committed.
Results are written up in audits/mdrm_check.md.
"""

import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip"
ZIP_PATH = ROOT / "temp" / "MDRM.zip"
AS_OF = pd.Timestamp("2022-12-31")
FORMS = ["FFIEC 031", "FFIEC 041", "FFIEC 051"]  # the three call report forms

# The codes used in code/02_build_bank_measures.py (FIELDS).
CODES = ["RCFD2170", "RCON2170", "RCFD3210", "RCON3210", "RCON2200", "RCON5597",
         "RCFD1754", "RCON1754", "RCFD1771", "RCON1771",
         "RCFD1772", "RCON1772", "RCFD1773", "RCON1773"]

# Download the dictionary once (it is about 8 MB).
if not ZIP_PATH.exists():
    ZIP_PATH.parent.mkdir(exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (course project)"})
    ZIP_PATH.write_bytes(urllib.request.urlopen(req).read())

# Read the CSV inside the zip. Its first line is a title ("PUBLIC"), so skip it.
with zipfile.ZipFile(ZIP_PATH) as z:
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    mdrm = pd.read_csv(io.BytesIO(z.read(name)), skiprows=1, dtype=str, encoding="latin-1")

mdrm["code"] = mdrm["Mnemonic"].str.strip() + mdrm["Item Code"].str.strip()
# End date 12/31/9999 means "still in force"; it is too far out for pandas, so it
# becomes NaT and is then treated as open-ended.
fmt = "%m/%d/%Y %I:%M:%S %p"
mdrm["start"] = pd.to_datetime(mdrm["Start Date"], format=fmt, errors="coerce")
mdrm["end"] = pd.to_datetime(mdrm["End Date"], format=fmt, errors="coerce").fillna(pd.Timestamp.max)

# Keep call report entries that were in force on 12/31/2022.
live = mdrm[mdrm["code"].isin(CODES) & mdrm["Reporting Form"].isin(FORMS)
            & (mdrm["start"] <= AS_OF) & (mdrm["end"] >= AS_OF)]

# One line per code: its name and which call report forms carry it.
table = (live.groupby("code")
             .agg(item_name=("Item Name", "first"),
                  forms=("Reporting Form", lambda f: ", ".join(sorted(set(f)))))
             .reindex(CODES))
print(f"MDRM file: {name}")
print(table.to_string())

missing = table[table["item_name"].isna()].index.tolist()
print("\nCodes with no call report entry on 12/31/2022:", missing or "none")
