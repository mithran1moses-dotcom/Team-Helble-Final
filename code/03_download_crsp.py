"""
03_download_crsp.py

Pulls CRSP daily stock returns from WRDS for the 12 v0 banks plus SPY (the market
index for the event study), Jan 2022 to Jun 2023. All returns now come from this
one source (see DECISIONS.md, "Data source").

Banks are matched by CRSP identifiers, never by ticker (delisted tickers get reused):
    ticker -> holding company name (inputs/links/v0_banks.csv)
           -> PERMCO   (NY Fed CRSP-FRB link file, link valid on 12/31/2022)
           -> PERMNO   (CRSP stocknames: the company's common share, shrcd 10/11)
SPY is an ETF with no PERMCO in the bank link file, so it is fixed by its PERMNO
(84398) and checked against CRSP stocknames.

Inputs : inputs/links/v0_banks.csv
         inputs/links/raw/crsp_20240930v2.csv   (code/01a_download_nyfed_link.py)
Outputs (all git-ignored: the WRDS license forbids redistributing CRSP data):
         inputs/prices/crsp/crsp_names.csv        stocknames rows for the 13 PERMNOs
         inputs/prices/crsp/crsp_dsf.csv          daily returns (crsp.dsf)
         inputs/prices/crsp/crsp_delist.csv       delisting returns (crsp.dsedelist)
         inputs/prices/crsp/crsp_permno_map.csv   ticker -> permco -> permno used by 04
         inputs/prices/crsp/crsp_pull.provenance.txt   source, tables, date pulled

Login: the script asks for your WRDS username and password each time and passes
them straight to the connection. Nothing is written to disk (it never creates a
.pgpass file). WRDS may also send a Duo push to approve.
"""

import getpass
from datetime import date
from pathlib import Path

import pandas as pd
import wrds

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inputs" / "prices" / "crsp"
START, END = "2022-01-01", "2023-06-30"
AS_OF = 20221231          # link date, same as code/01b_build_link_table.py
SPY_PERMNO = 84398        # SPDR S&P 500 ETF Trust in CRSP
TABLES = ["crsp.stocknames", "crsp.dsf", "crsp.dsedelist"]

# 1. PERMCO for each v0 ticker: match the holding-company name to the NY Fed
#    CRSP-FRB file (same name key and date filter as code/01b_build_link_table.py).
banks = pd.read_csv(ROOT / "inputs" / "links" / "v0_banks.csv")
nyfed = pd.read_csv(ROOT / "inputs" / "links" / "raw" / "crsp_20240930v2.csv")
nyfed = nyfed[(nyfed["dt_start"] <= AS_OF) & (nyfed["dt_end"] >= AS_OF)]
banks = banks.merge(nyfed[["name", "permco"]], left_on="nyfed_name", right_on="name",
                    how="left", validate="1:1")
assert banks["permco"].notna().all() and banks["permco"].is_unique and len(banks) == 12
banks["permco"] = banks["permco"].astype(int)

# 2. Log in. Credentials are typed at the prompt and kept only in memory.
username = input("WRDS username: ").strip()
password = getpass.getpass("WRDS password: ")
db = wrds.Connection(wrds_username=username, wrds_password=password)
del password

# 3. Company names and share codes for these PERMCOs and for SPY, keeping only
#    name records that overlap the sample window.
permcos = ", ".join(str(p) for p in banks["permco"])
names = db.raw_sql(f"""
    select permno, permco, ticker, comnam, shrcd, exchcd, namedt, nameenddt
    from crsp.stocknames
    where (permco in ({permcos}) or permno = {SPY_PERMNO})
      and namedt <= '{END}' and nameenddt >= '{START}'
""")

# 4. Map PERMCO -> PERMNO: each bank must have exactly one common-share PERMNO
#    (share code 10 or 11) in the window. Preferred shares and other classes drop out.
common = names[names["shrcd"].isin([10, 11]) & names["permco"].isin(banks["permco"])]
pmap = common[["permco", "permno"]].drop_duplicates()
assert pmap["permco"].is_unique, f"a bank has more than one common PERMNO:\n{pmap}"
pmap = banks[["ticker", "permco"]].merge(pmap, on="permco", how="left", validate="1:1")
assert pmap["permno"].notna().all(), f"no common PERMNO for {pmap.loc[pmap['permno'].isna(), 'ticker'].tolist()}"

# 5. Add SPY, after checking that PERMNO 84398 really is SPY in the window.
spy = names[names["permno"] == SPY_PERMNO]
assert (spy["ticker"] == "SPY").all() and len(spy) > 0, f"PERMNO {SPY_PERMNO} is not SPY:\n{spy}"
pmap = pd.concat([pmap, pd.DataFrame({"ticker": ["SPY"], "permco": [spy["permco"].iloc[0]],
                                      "permno": [SPY_PERMNO]})])
pmap["permno"] = pmap["permno"].astype(int)
assert pmap["permno"].is_unique and pmap["ticker"].is_unique and len(pmap) == 13
permnos = ", ".join(str(p) for p in pmap["permno"])

# 6. Daily returns. RET is the holding-period return including dividends.
dsf = db.raw_sql(f"""
    select permno, permco, date, ret, retx, prc
    from crsp.dsf
    where permno in ({permnos}) and date between '{START}' and '{END}'
""", date_cols=["date"])
assert not dsf.duplicated(["permno", "date"]).any()

# 7. Delisting records (for SIVB: the return from its last price to its
#    post-delisting value). Code 04 applies DLRET on the delisting date.
delist = db.raw_sql(f"""
    select permno, dlstdt, dlstcd, dlret, dlretx, dlprc
    from crsp.dsedelist
    where permno in ({permnos})
""", date_cols=["dlstdt"])
db.close()

# 8. Save the raw pulls and the map, then a provenance note.
OUT.mkdir(parents=True, exist_ok=True)
names.to_csv(OUT / "crsp_names.csv", index=False)
dsf.sort_values(["permno", "date"]).to_csv(OUT / "crsp_dsf.csv", index=False)
delist.to_csv(OUT / "crsp_delist.csv", index=False)
pmap.to_csv(OUT / "crsp_permno_map.csv", index=False)
(OUT / "crsp_pull.provenance.txt").write_text(
    f"Source: CRSP via WRDS (PostgreSQL), Python package wrds {wrds.__version__}\n"
    f"Tables: {', '.join(TABLES)}\n"
    f"Window: {START} to {END}\n"
    f"Pulled: {date.today()}\n"
    f"PERMCO source: inputs/links/raw/crsp_20240930v2.csv (links valid on {AS_OF})\n"
    f"PERMNOs: {', '.join(f'{t}={p}' for t, p in zip(pmap['ticker'], pmap['permno']))}\n"
    f"Rows: crsp.dsf {len(dsf)}, crsp.dsedelist {len(delist)}, crsp.stocknames {len(names)}\n")

print(pmap.to_string(index=False))
print(f"Wrote {len(dsf)} daily rows and {len(delist)} delisting rows to {OUT.relative_to(ROOT)}/")
print("Delisting records:")
print(delist.to_string(index=False))
