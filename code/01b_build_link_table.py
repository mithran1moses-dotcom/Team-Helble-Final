"""
01b_build_link_table.py

Builds the v0 link table: one row per bank subsidiary of each of the 12 v0
bank holding companies (BHCs), as of 12/31/2022.

Inputs:
    inputs/links/v0_banks.csv                  hand-entered: ticker -> name as written in the NY Fed file
    inputs/links/raw/crsp_20240930v2.csv       NY Fed CRSP-FRB link file (code/01a_download_nyfed_link.py)
    inputs/links/raw/nic/CSV_RELATIONSHIPS.CSV       FFIEC NIC, manual download (see inputs/links/README.md)
    inputs/links/raw/nic/CSV_ATTRIBUTES_ACTIVE.CSV
    inputs/links/raw/nic/CSV_ATTRIBUTES_CLOSED.CSV
Output:
    inputs/links/bank_link_v0.csv   (every row must be hand-checked; checked_by is left blank)
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LINKS = ROOT / "inputs" / "links"
NIC = LINKS / "raw" / "nic"
OUT = LINKS / "bank_link_v0.csv"
AS_OF = 20221231  # last call report date before SVB failed

# Safety check: never overwrite a link table someone has already hand-checked.
if OUT.exists():
    old = pd.read_csv(OUT, dtype=str)
    assert old["checked_by"].isna().all(), (
        f"{OUT.name} has hand-checked rows. Rename or delete it on purpose before rebuilding.")

# 1. The 12 v0 tickers, with the holding-company name exactly as the NY Fed file spells it.
banks = pd.read_csv(LINKS / "v0_banks.csv")
assert banks["ticker"].is_unique and len(banks) == 12

# 2. NY Fed CRSP-FRB file: keep links valid on 12/31/2022. The file has no tickers,
#    so we match on name; "entity" is the holding company's RSSD.
nyfed = pd.read_csv(LINKS / "raw" / "crsp_20240930v2.csv")
nyfed = nyfed[(nyfed["dt_start"] <= AS_OF) & (nyfed["dt_end"] >= AS_OF)]
assert nyfed["name"].is_unique
banks = banks.merge(nyfed, left_on="nyfed_name", right_on="name", how="left", validate="1:1")
assert banks["entity"].notna().all(), banks.loc[banks["entity"].isna(), "ticker"].tolist()
banks = banks.rename(columns={"entity": "bhc_rssd"})
assert banks["bhc_rssd"].is_unique

# 3. NIC attributes: one row per institution (its latest record), from the active
#    and closed files. Closed is needed for SVB and Comerica, which no longer exist.
cols = ["#ID_RSSD", "NM_LGL", "ENTITY_TYPE", "ID_FDIC_CERT"]
attrs = pd.concat([pd.read_csv(NIC / "CSV_ATTRIBUTES_ACTIVE.CSV", usecols=cols),
                   pd.read_csv(NIC / "CSV_ATTRIBUTES_CLOSED.CSV", usecols=cols)])
attrs = attrs.rename(columns={"#ID_RSSD": "rssd", "NM_LGL": "name",
                              "ENTITY_TYPE": "entity_type", "ID_FDIC_CERT": "fdic_cert"})
attrs["name"] = attrs["name"].str.strip()
assert attrs["rssd"].is_unique

# 4. NIC relationships: keep "controls" links (CTRL_IND = 1) in force on 12/31/2022.
rels = pd.read_csv(NIC / "CSV_RELATIONSHIPS.CSV",
                   usecols=["#ID_RSSD_PARENT", "ID_RSSD_OFFSPRING", "CTRL_IND", "DT_START", "DT_END"])
rels = rels[(rels["CTRL_IND"] == 1) & (rels["DT_START"] <= AS_OF) & (rels["DT_END"] >= AS_OF)]
rels = rels.rename(columns={"#ID_RSSD_PARENT": "parent", "ID_RSSD_OFFSPRING": "child"})

# 5. For each holding company, walk down the ownership tree level by level to find
#    everything it controls, including banks held through intermediate companies.
#    We record each entity's parent so step 6 can tell where it sits in the tree.
#    The holding company itself is included (parent = none), because Zions is a
#    bank with no holding company above it.
rows = []
for bhc in banks.itertuples():
    rows.append({"ticker": bhc.ticker, "bhc_rssd": bhc.bhc_rssd, "bank_rssd": bhc.bhc_rssd, "parent_rssd": None})
    found = {bhc.bhc_rssd}
    level = [bhc.bhc_rssd]
    while level:
        links_down = rels[rels["parent"].isin(level) & ~rels["child"].isin(found)]
        links_down = links_down.drop_duplicates("child")  # an entity can have two controlling parents; keep one
        for link_row in links_down.itertuples():
            rows.append({"ticker": bhc.ticker, "bhc_rssd": bhc.bhc_rssd,
                         "bank_rssd": link_row.child, "parent_rssd": link_row.parent})
        level = links_down["child"].tolist()
        found.update(level)
tree = pd.DataFrame(rows)
tree = tree.merge(attrs, left_on="bank_rssd", right_on="rssd", how="left", validate="m:1")

# 6. Keep the entities that file their own call report, without double counting:
#    (a) FDIC-insured institutions (they have an FDIC certificate number), unless
#        their parent is itself an insured bank: a bank's call report already
#        consolidates the banks it owns, so adding them again would count them twice.
#    (b) Entities NIC publishes no record for, but only when the holding company
#        owns them directly (this catches Comerica Bank and MUFG Union Bank).
#        Unrecorded entities further down sit inside a bank's consolidated report.
#    Every row is hand-checked, and Step 2 confirms each bank_rssd is a call report filer.
insured_rssd = set(attrs.loc[attrs["fdic_cert"] > 0, "rssd"])
is_insured = tree["bank_rssd"].isin(insured_rssd)
parent_is_bank = tree["parent_rssd"].isin(insured_rssd)
no_record_under_bhc = tree["name"].isna() & (tree["parent_rssd"] == tree["bhc_rssd"])
link = tree[(is_insured & ~parent_is_bank) | no_record_under_bhc].copy()

# Print what rule (a) dropped, so the hand-check can confirm each one.
dropped = tree[is_insured & parent_is_bank]
print("Dropped as consolidated into a parent bank:")
print(dropped[["ticker", "bank_rssd", "name", "parent_rssd"]].to_string(index=False))

# 7. Holding-company names come from NIC too.
bhc_names = attrs.rename(columns={"rssd": "bhc_rssd", "name": "bhc_name"})[["bhc_rssd", "bhc_name"]]
link = link.merge(bhc_names, on="bhc_rssd", how="left", validate="m:1")

# 8. Notes for the hand-check. Every row starts with HAND-CHECK.
link["notes"] = "HAND-CHECK: ticker->bhc_rssd by name match to NY Fed file; bank found via NIC control links"
link.loc[link["bank_rssd"] == link["bhc_rssd"], "notes"] += "; BHC is itself the bank (no holding company)"
link.loc[link["name"].isna(), "notes"] += "; NIC has no attribute record for this bank: name blank, fill by hand"
link.loc[link["entity_type"].isin(["NTC"]), "notes"] += "; insured trust company, small; check it files a call report"
link["link_source"] = "NY Fed CRSP-FRB crsp_20240930v2 + FFIEC NIC relationships as of 2022-12-31"
link["checked_by"] = ""
link["checked_on"] = ""

# 9. Final layout, one row per (holding company, bank subsidiary).
link = link.rename(columns={"name": "bank_name"})
link = link[["ticker", "bhc_name", "bhc_rssd", "bank_rssd", "bank_name",
             "link_source", "checked_by", "checked_on", "notes"]]
link = link.sort_values(["ticker", "bank_rssd"]).reset_index(drop=True)
assert link["bank_rssd"].is_unique, "a bank is linked to two holding companies"
assert set(link["ticker"]) == set(banks["ticker"]), "a holding company has no bank"

link.to_csv(OUT, index=False)
print(f"Wrote {OUT.relative_to(ROOT)}: {len(link)} bank subsidiaries for {link['ticker'].nunique()} holding companies")
print(link[["ticker", "bhc_rssd", "bank_rssd", "bank_name"]].to_string(index=False))
