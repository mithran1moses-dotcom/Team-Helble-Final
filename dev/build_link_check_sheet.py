"""
build_link_check_sheet.py: gather independent evidence for hand-checking
inputs/links/bank_link_v0.csv, row by row.

    python dev/build_link_check_sheet.py

Our link table was built from the NY Fed CRSP-FRB file and FFIEC NIC. This
script checks it against a third source, the FDIC BankFind API
(https://api.fdic.gov/banks/), using each bank's 12/31/2022 quarterly record:
    1. Does the FDIC put the bank under the same holding company (RSSDHCR)?
    2. Does the FDIC's total assets match our call report total assets?
    3. Completeness: which FDIC-insured banks does the FDIC place under our 12
       holding companies on 12/31/2022, and are any missing from our table?

It does NOT replace the hand-check. A person still reviews each row (see
audits/link_check_sheet.md) and fills checked_by / checked_on in the link table.

Inputs : inputs/links/bank_link_v0.csv, outputs/bank_measures_2022Q4.csv
Output : audits/link_check_fdic.csv (one row per link-table row, with the FDIC evidence)
         audits/link_check_fdic_universe.csv (every FDIC bank under our 12 holding companies)
"""

import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.fdic.gov/banks/"
REPDTE = "20221231"
FIELDS = "REPDTE,CERT,NAME,RSSDHCR,NAMEHCR,ASSET"


def fdic(endpoint: str, filters: str, fields: str, limit: int = 100) -> list[dict]:
    """Call one FDIC API endpoint and return the list of records."""
    query = urllib.parse.urlencode({"filters": filters, "fields": fields, "limit": limit})
    req = urllib.request.Request(API + endpoint + "?" + query,
                                 headers={"User-Agent": "Mozilla/5.0 (course project)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return [r["data"] for r in json.load(resp)["data"]]


# 1. Our link table, plus each bank's FDIC certificate and total assets from our call report data.
link = pd.read_csv(ROOT / "inputs" / "links" / "bank_link_v0.csv")
banks = pd.read_csv(ROOT / "outputs" / "bank_measures_2022Q4.csv",
                    usecols=["bank_rssd", "bank_name", "fdic_cert", "filing_type", "total_assets"])
banks = banks.rename(columns={"bank_name": "callreport_name", "total_assets": "callreport_assets"})
sheet = link.merge(banks, on="bank_rssd", how="left", validate="1:1")
assert len(sheet) == len(link)

# 2. FDIC evidence for each linked bank.
#    Call report filers: the 12/31/2022 quarterly record, found by FDIC certificate.
#    Non-filers: the FDIC institution record by RSSD (latest status, not as of 2022).
rows = []
for r in sheet.itertuples():
    ev = {"bank_rssd": r.bank_rssd}
    if pd.notna(r.fdic_cert) and r.fdic_cert > 0:
        recs = fdic("financials", f"CERT:{int(r.fdic_cert)} AND REPDTE:{REPDTE}", FIELDS)
        if recs:
            ev.update({"fdic_name": recs[0]["NAME"], "fdic_holder_rssd": int(recs[0]["RSSDHCR"] or 0),
                       "fdic_holder_name": recs[0]["NAMEHCR"], "fdic_assets": recs[0]["ASSET"],
                       "fdic_source": f"financials, REPDTE {REPDTE}"})
    else:
        recs = fdic("institutions", f"FED_RSSD:{r.bank_rssd}", "NAME,CERT,RSSDHCR,NAMEHCR,ACTIVE")
        ev["fdic_source"] = ("institutions (latest record)" if recs
                             else "not in FDIC data (not FDIC-insured)")
        if recs:
            ev.update({"fdic_name": recs[0]["NAME"], "fdic_holder_rssd": int(recs[0]["RSSDHCR"] or 0),
                       "fdic_holder_name": recs[0]["NAMEHCR"]})
    rows.append(ev)
sheet = sheet.merge(pd.DataFrame(rows), on="bank_rssd", how="left", validate="1:1")

# 3. Automatic comparisons. A bank with no holding company (Zions) has RSSDHCR 0 at the FDIC.
holder_expected = sheet["bhc_rssd"].where(sheet["bhc_rssd"] != sheet["bank_rssd"], 0)
sheet["holder_match"] = sheet["fdic_holder_rssd"] == holder_expected
# Assets are in $ thousands in both sources; allow $1K of rounding. Blank when the FDIC has no figure.
assets_close = (sheet["fdic_assets"] - sheet["callreport_assets"]).abs() <= 1
sheet["assets_match"] = assets_close.astype("boolean").mask(sheet["fdic_assets"].isna())
sheet["nic_profile_url"] = ("https://www.ffiec.gov/npw/Institution/Profile/"
                            + sheet["bank_rssd"].astype(str) + "?dt=" + REPDTE)
sheet["pulled_on"] = date.today().isoformat()

out = ROOT / "audits" / "link_check_fdic.csv"
sheet.to_csv(out, index=False)
print(f"Wrote {out.relative_to(ROOT)}")
print(sheet[["ticker", "bank_rssd", "callreport_name", "fdic_holder_rssd", "bhc_rssd",
             "holder_match", "assets_match", "fdic_source"]].to_string(index=False))

# 4. Completeness: every insured bank the FDIC places under one of our holding companies.
#    Zions has no holding company, so it is checked by its own certificate instead.
holders = " OR ".join(str(x) for x in sorted(set(link["bhc_rssd"]) - set(link["bank_rssd"])))
universe = pd.DataFrame(fdic("financials", f"RSSDHCR:({holders}) AND REPDTE:{REPDTE}", FIELDS))
universe["CERT"] = universe["CERT"].astype(int)
universe["in_our_link_table"] = universe["CERT"].isin(sheet["fdic_cert"].dropna().astype(int))
out_u = ROOT / "audits" / "link_check_fdic_universe.csv"
universe.sort_values(["RSSDHCR", "CERT"]).to_csv(out_u, index=False)
print(f"\nWrote {out_u.relative_to(ROOT)}: {len(universe)} FDIC-insured banks under our holding companies")
print(universe[["NAMEHCR", "CERT", "NAME", "ASSET", "in_our_link_table"]].to_string(index=False))
