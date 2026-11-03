"""
Writes tiny FAKE call-report files in the real FFIEC bulk format
(row 1 = MDRM codes, row 2 = descriptions, schedules split into parts)
so 02_build_bank_measures.py can be tested before the real download exists.

    python dev/make_fake_call_reports.py
    python code/02_build_bank_measures.py FAKE 12312022

Numbers are invented. Never use outputs/bank_measures_FAKE.csv for analysis.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "inputs" / "call_reports" / "FAKE"
P = "12312022"


def write(name, header, desc, rows):
    lines = ["\t".join(f'"{h}"' for h in header),
             "\t".join(f'"{d}"' for d in desc)]
    lines += ["\t".join(str(v) for v in r) for r in rows]
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="latin-1")


OUT.mkdir(parents=True, exist_ok=True)

# Bank 1: big 031 filer (RCFD). Bank 2: SVB-like 041 filer (RCON only).
# Bank 3: small 051 filer, no uninsured-deposit field reported.
write(f"FFIEC CDR Call Bulk POR {P}.txt",
      ["IDRSSD", "FDIC Certificate Number", "Financial Institution Name",
       "Financial Institution State", "Financial Institution Filing Type"],
      ["", "", "", "", ""],
      [[1, 101, "FAKE BIG BANK NA", "NY", "031"],
       [2, 102, "FAKE REGIONAL BANK", "CA", "041"],
       [3, 103, "FAKE COMMUNITY BANK", "PA", "051"]])

write(f"FFIEC CDR Call Schedule RC {P}.txt",
      ["IDRSSD", "RCFD2170", "RCON2170", "RCFD3210", "RCON3210", "RCON2200"],
      ["", "TOTAL ASSETS", "TOTAL ASSETS", "TOTAL BANK EQUITY CAPITAL",
       "TOTAL BANK EQUITY CAPITAL", "TOTAL DEPOSITS"],
      [[1, 3000000, 2500000, 250000, "", 2000000],
       [2, "", 200000, 15000, 15000, 170000],
       [3, "", 800, "", 80, 700]])

write(f"FFIEC CDR Call Schedule RCB {P}(1 of 2).txt",
      ["IDRSSD", "RCFD1754", "RCON1754", "RCFD1771", "RCON1771"],
      ["", "HTM AMORTIZED COST", "HTM AMORTIZED COST",
       "HTM FAIR VALUE", "HTM FAIR VALUE"],
      [[1, 400000, "", 360000, ""],
       [2, "", 90000, "", 75000],
       [3, "", 0, "", 0]])

write(f"FFIEC CDR Call Schedule RCB {P}(2 of 2).txt",
      ["IDRSSD", "RCFD1772", "RCON1772", "RCFD1773", "RCON1773"],
      ["", "AFS AMORTIZED COST", "AFS AMORTIZED COST",
       "AFS FAIR VALUE", "AFS FAIR VALUE"],
      [[1, 300000, "", 280000, ""],
       [2, "", 30000, "", 27000],
       [3, "", 200, "", 190]])

write(f"FFIEC CDR Call Schedule RCO {P}.txt",
      ["IDRSSD", "RCON5597"],
      ["", "ESTIMATED AMOUNT OF UNINSURED DEPOSITS"],
      [[1, 900000], [2, 150000], [3, ""]])

print(f"Wrote fake files to {OUT.relative_to(ROOT)}")
