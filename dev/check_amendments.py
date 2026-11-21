"""
check_amendments.py: which 12/31/2022 call reports were changed after the event?

    python dev/check_amendments.py

Why (self-audit finding 10, v1 plan task 6): the FFIEC bulk file we use is the
current version of each bank's 12/31/2022 call report ("CDR data as of
2026-09-15"). If a bank resubmitted that report after Mar 9, 2023 (day 0), our
numbers can differ from what the market saw. On Jul 24, 2023 the FDIC told
banks to correct how they report uninsured deposits (RCON5597), our main
measure, so resubmissions after that date matter most.

The Panel of Reporters (POR) file has one date per bank: "Last Date/Time
Submission Updated On". It shows WHEN a bank last resubmitted, not WHAT changed,
and it keeps only the latest date. So a date after Mar 9, 2023 says "may differ
from the version the market saw", not "did change".

Inputs : inputs/call_reports/2022Q4/FFIEC CDR Call Bulk POR 12312022.txt
         inputs/links/bank_link_v0.csv, outputs/bank_measures_2022Q4.csv
Outputs: audits/amendments_check.csv          one row per link-table bank
         audits/amendments_check_summary.csv  counts for our banks and for all filers
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
POR = ROOT / "inputs" / "call_reports" / "2022Q4" / "FFIEC CDR Call Bulk POR 12312022.txt"
UPDATED = "Last Date/Time Submission Updated On"
EVENT_DAY = pd.Timestamp("2023-03-09")   # day 0: anything later the market had not seen
FDIC_LETTER = pd.Timestamp("2023-07-24")  # FDIC letter on reporting uninsured deposits

# 1. Read the POR file: one row per filing bank, with its last-resubmission date.
#    Row 2 of FFIEC files is a text description, so keep rows with a numeric IDRSSD.
por = pd.read_csv(POR, sep="\t", dtype=str, encoding="latin-1")
por.columns = [c.strip().strip('"') for c in por.columns]
por["bank_rssd"] = pd.to_numeric(por["IDRSSD"], errors="coerce")
por = por.dropna(subset=["bank_rssd"]).astype({"bank_rssd": "int64"})
por["last_updated"] = pd.to_datetime(por[UPDATED])
assert por["bank_rssd"].is_unique and por["last_updated"].notna().all()

# 2. Flag resubmissions after day 0 and after the FDIC letter.
por["updated_after_event"] = por["last_updated"] > EVENT_DAY
por["updated_after_fdic_letter"] = por["last_updated"] > FDIC_LETTER

# 3. Our banks: attach the dates to the link table. The two trust companies
#    that file no call report get no date.
link = pd.read_csv(ROOT / "inputs" / "links" / "bank_link_v0.csv")
ours = link[["ticker", "bhc_rssd", "bank_rssd", "bank_name"]].merge(
    por[["bank_rssd", "last_updated", "updated_after_event", "updated_after_fdic_letter"]],
    on="bank_rssd", how="left", validate="1:1")
filers = ours.dropna(subset=["last_updated"])
assert len(filers) == 19, f"expected 19 filing banks, got {len(filers)}"

# 4. Add each bank's share of its holding company's total assets, so we can see
#    whether the resubmitted bank is the main bank or a small one.
assets = pd.read_csv(ROOT / "outputs" / "bank_measures_2022Q4.csv")[["bank_rssd", "total_assets"]]
ours = ours.merge(assets, on="bank_rssd", how="left", validate="1:1")
ours["share_of_bhc_assets"] = ours["total_assets"] / ours.groupby("ticker")["total_assets"].transform("sum")
ours = ours.sort_values(["ticker", "bank_rssd"])
ours.to_csv(ROOT / "audits" / "amendments_check.csv", index=False)

# 5. Summary counts: our 19 filing banks, our 12 holding companies (any bank
#    resubmitted after the date), every filer, and every filer with >= $1B in
#    assets (the banks that report uninsured deposits; the v1 universe is in this group).
all_filers = por.merge(assets, on="bank_rssd", how="left", validate="1:1")
big = all_filers[all_filers["total_assets"] >= 1_000_000]  # $ thousands, so $1B
bhc = ours.dropna(subset=["last_updated"]).groupby("ticker")[
    ["updated_after_event", "updated_after_fdic_letter"]].any()
rows = []
for name, df in [("our filing banks", filers), ("our holding companies (any bank)", bhc),
                 ("all filers", all_filers), ("all filers with assets >= $1B", big)]:
    rows.append({"group": name, "n": len(df),
                 "n_updated_after_event": int(df["updated_after_event"].sum()),
                 "n_updated_after_fdic_letter": int(df["updated_after_fdic_letter"].sum())})
summary = pd.DataFrame(rows)
summary["share_after_event"] = summary["n_updated_after_event"] / summary["n"]
summary.to_csv(ROOT / "audits" / "amendments_check_summary.csv", index=False)

print(ours[["ticker", "bank_name", "last_updated", "updated_after_event",
            "updated_after_fdic_letter", "share_of_bhc_assets"]].round(3).to_string(index=False))
print()
print(summary.round(3).to_string(index=False))
print("Wrote audits/amendments_check.csv and audits/amendments_check_summary.csv")
