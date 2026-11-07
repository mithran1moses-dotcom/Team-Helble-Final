"""
02_build_bank_measures.py

Builds the fragility measures from one quarter of FFIEC Call Report bulk data,
first for every bank, then for each v0 bank holding company (BHC) by summing
its bank subsidiaries.

Inputs : inputs/call_reports/<LABEL>/        (see inputs/call_reports/README.md)
         inputs/links/bank_link_v0.csv       (code/01b_build_link_table.py)
         For LABEL = FAKE, the fake link file written by dev/make_fake_call_reports.py.
Outputs: outputs/bank_measures_<LABEL>.csv   one row per bank (bank_rssd)
         outputs/bhc_measures_<LABEL>.csv    one row per holding company (bhc_rssd)

Usage:
    python code/02_build_bank_measures.py                 # defaults to 2022Q4 / 12312022
    python code/02_build_bank_measures.py FAKE 12312022   # test on fake data

Measures (all from Schedules RC, RC-B, RC-O, in $ thousands as reported):
    total_assets         2170   (RC)
    total_equity         3210   (RC)   total bank equity capital
    total_deposits       RCON2200 (RC)  deposits in domestic offices
    uninsured_deposits   RCON5597 (RC-O Memo 2) estimated uninsured deposits;
                         only reported by banks with >= $1B in assets -> NaN otherwise
    htm_amortized_cost   1754   (RC-B)
    htm_fair_value       1771   (RC-B)
    afs_amortized_cost   1772   (RC-B)
    afs_fair_value       1773   (RC-B)

    htm_loss                  = htm_amortized_cost - htm_fair_value  (positive = loss)
    afs_loss                  = afs_amortized_cost - afs_fair_value  (positive = loss)
    unreal_loss               = htm_loss + afs_loss
    unreal_loss_to_adj_equity = unreal_loss / (total_equity + afs_loss)   MAIN measure
                                (AFS losses are already deducted from equity, so we add them back;
                                 Jiang, Matvos, Piskorski & Seru 2023)
    htm_loss_to_equity        = htm_loss / total_equity                   robustness
    uninsured_dep_share       = uninsured_deposits / total_deposits

Holding-company rule (DECISIONS.md): sum the dollar amounts across a BHC's
banks first, then compute the ratios from the sums.

VERIFY every MDRM code against the FFIEC data dictionary / report form
instructions for the period you pulled before trusting the output.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Field map: variable -> (list of MDRM codes in priority order, schedule code)
# Schedule code is the token that appears in the bulk file name,
# e.g. "FFIEC CDR Call Schedule RCB 12312022(1 of 2).txt" -> "RCB".
# RCFD (consolidated, 031 filers) is preferred; RCON is the fallback.
# ---------------------------------------------------------------------------
FIELDS: dict[str, tuple[list[str], str]] = {
    "total_assets":       (["RCFD2170", "RCON2170"], "RC"),
    "total_equity":       (["RCFD3210", "RCON3210"], "RC"),
    "total_deposits":     (["RCON2200"],             "RC"),
    "uninsured_deposits": (["RCON5597"],             "RCO"),
    "htm_amortized_cost": (["RCFD1754", "RCON1754"], "RCB"),
    "htm_fair_value":     (["RCFD1771", "RCON1771"], "RCB"),
    "afs_amortized_cost": (["RCFD1772", "RCON1772"], "RCB"),
    "afs_fair_value":     (["RCFD1773", "RCON1773"], "RCB"),
}
DOLLAR_COLS = list(FIELDS)  # the amounts we sum to the holding company


def read_bulk_file(path: Path) -> pd.DataFrame:
    """Read one FFIEC bulk .txt file.

    Row 1 = MDRM codes, row 2 = text descriptions (dropped). Everything is read
    as string first so IDs and blanks aren't mangled; numeric conversion
    happens later, only for the columns we use.
    """
    df = pd.read_csv(path, sep="\t", dtype=str, low_memory=False,
                     encoding="latin-1")
    df.columns = [c.strip().strip('"') for c in df.columns]
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]  # trailing-tab artifact
    # Drop the description row (and any other non-data row): IDRSSD must be numeric
    df["IDRSSD"] = pd.to_numeric(df["IDRSSD"].str.strip().str.strip('"'),
                                 errors="coerce")
    df = df.dropna(subset=["IDRSSD"]).copy()
    df["IDRSSD"] = df["IDRSSD"].astype("int64")
    return df


def read_schedule(folder: Path, schedule: str, period: str) -> pd.DataFrame:
    """Read all parts of one schedule and combine them side by side on IDRSSD."""
    pattern = f"FFIEC CDR Call Schedule {schedule} {period}*.txt"
    parts = sorted(folder.glob(pattern))
    if not parts:
        raise FileNotFoundError(f"No files match '{pattern}' in {folder}")

    out = None
    for p in parts:
        df = read_bulk_file(p)
        assert df["IDRSSD"].is_unique, f"duplicate IDRSSD in {p.name}"
        if out is None:
            out = df
        else:
            new_cols = ["IDRSSD"] + [c for c in df.columns if c not in out.columns]
            out = out.merge(df[new_cols], on="IDRSSD", how="outer",
                            validate="1:1")
    return out


def read_por(folder: Path, period: str) -> pd.DataFrame:
    """Panel of Reporters: bank names, FDIC cert, filing type (031/041/051)."""
    parts = sorted(folder.glob(f"FFIEC CDR Call Bulk POR {period}*.txt"))
    if not parts:
        raise FileNotFoundError(f"No POR file for {period} in {folder}")
    por = read_bulk_file(parts[0])
    keep = {
        "IDRSSD": "bank_rssd",
        "Financial Institution Name": "bank_name",
        "FDIC Certificate Number": "fdic_cert",
        "Financial Institution State": "state",
        "Financial Institution Filing Type": "filing_type",
    }
    present = {k: v for k, v in keep.items() if k in por.columns}
    missing = set(keep) - set(present)
    if missing:
        print(f"  note: POR columns not found (check names): {sorted(missing)}")
    return por[list(present)].rename(columns=present)


def pick_first_available(df: pd.DataFrame, codes: list[str]) -> pd.Series:
    """Return the first non-missing value across codes (RCFD before RCON)."""
    result = pd.Series(np.nan, index=df.index, dtype="float64")
    for code in codes:
        if code in df.columns:
            vals = pd.to_numeric(df[code].str.strip().str.strip('"'),
                                 errors="coerce")
            result = result.fillna(vals)
    return result


def add_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Compute losses and ratios from the dollar amounts.

    Used for both banks and holding companies, so both levels use one formula.
    A missing HTM or AFS amount is treated as no securities of that type (0 loss).
    Denominators that are zero or negative give NaN instead of a misleading ratio.
    """
    df["htm_loss"] = df["htm_amortized_cost"] - df["htm_fair_value"]
    df["afs_loss"] = df["afs_amortized_cost"] - df["afs_fair_value"]
    htm = df["htm_loss"].fillna(0)
    afs = df["afs_loss"].fillna(0)
    df["unreal_loss"] = htm + afs

    adj_equity = df["total_equity"] + afs
    df["unreal_loss_to_adj_equity"] = df["unreal_loss"] / adj_equity.where(adj_equity > 0)
    df["htm_loss_to_equity"] = htm / df["total_equity"].where(df["total_equity"] > 0)
    df["uninsured_dep_share"] = df["uninsured_deposits"] / df["total_deposits"].where(df["total_deposits"] > 0)
    return df


def build_measures(folder: Path, period: str) -> pd.DataFrame:
    """One row per bank: the raw dollar amounts plus the ratios."""
    schedules = sorted({sched for _, sched in FIELDS.values()})
    raw = {s: read_schedule(folder, s, period) for s in schedules}

    out = read_por(folder, period)
    assert out["bank_rssd"].is_unique

    for var, (codes, sched) in FIELDS.items():
        src = raw[sched]
        found = [c for c in codes if c in src.columns]
        if not found:
            raise KeyError(f"{var}: none of {codes} found in schedule {sched}")
        col = pd.DataFrame({"bank_rssd": src["IDRSSD"],
                            var: pick_first_available(src, codes)})
        out = out.merge(col, on="bank_rssd", how="left", validate="1:1")

    out = add_ratios(out)
    out["report_period"] = period

    assert out["bank_rssd"].is_unique
    return out


def aggregate_to_bhc(banks: pd.DataFrame, link: pd.DataFrame, period: str) -> pd.DataFrame:
    """One row per holding company: sum its banks' dollar amounts, then compute ratios."""
    # Attach each linked bank's call report numbers. A linked bank that does not
    # file a call report (e.g. a non-insured-deposit trust company) is reported and dropped.
    link = link[["ticker", "bhc_name", "bhc_rssd", "bank_rssd"]]
    merged = link.merge(banks, on="bank_rssd", how="left", validate="1:1", indicator=True)
    not_filing = merged[merged["_merge"] == "left_only"]
    if len(not_filing):
        print("  Linked banks with no call report (dropped):")
        print(not_filing[["ticker", "bank_rssd"]].to_string(index=False))
    merged = merged[merged["_merge"] == "both"]

    # Count banks behind each holding company, and how many report uninsured deposits.
    # min_count=1 keeps the sum missing when none of a BHC's banks reports a value.
    bhc = merged.groupby(["bhc_rssd", "ticker", "bhc_name"], as_index=False).agg(
        n_banks=("bank_rssd", "count"),
        n_banks_uninsured_reported=("uninsured_deposits", "count"),
    )
    sums = merged.groupby("bhc_rssd")[DOLLAR_COLS].sum(min_count=1).reset_index()
    bhc = bhc.merge(sums, on="bhc_rssd", how="left", validate="1:1")

    bhc = add_ratios(bhc)
    bhc["report_period"] = period

    assert bhc["bhc_rssd"].is_unique and bhc["ticker"].is_unique
    assert set(bhc["ticker"]) == set(link["ticker"]), "a holding company lost all its banks"
    return bhc


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "2022Q4"
    period = sys.argv[2] if len(sys.argv) > 2 else "12312022"
    folder = ROOT / "inputs" / "call_reports" / label

    # Bank level: every bank in the call report data.
    banks = build_measures(folder, period)
    bank_path = ROOT / "outputs" / f"bank_measures_{label}.csv"
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    banks.to_csv(bank_path, index=False)
    print(f"Wrote {bank_path.relative_to(ROOT)}: {len(banks):,} banks")
    print(f"  with uninsured deposits reported: {banks['uninsured_deposits'].notna().sum():,}")

    # Holding-company level: the v0 banks, via the link table.
    if label == "FAKE":
        link_path = folder / "bank_link_FAKE.csv"
    else:
        link_path = ROOT / "inputs" / "links" / "bank_link_v0.csv"
    link = pd.read_csv(link_path)
    assert link["bank_rssd"].is_unique

    bhc = aggregate_to_bhc(banks, link, period)
    bhc_path = ROOT / "outputs" / f"bhc_measures_{label}.csv"
    bhc.to_csv(bhc_path, index=False)
    print(f"Wrote {bhc_path.relative_to(ROOT)}: {len(bhc)} holding companies")
    print(bhc[["ticker", "n_banks", "total_assets", "uninsured_dep_share",
               "unreal_loss_to_adj_equity", "htm_loss_to_equity"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
