"""
02_build_bank_measures.py

Builds one row per bank (IDRSSD) of the fragility measures from a single
quarter of FFIEC Call Report bulk data.

Input : inputs/call_reports/<PERIOD>/  (see inputs/call_reports/README.md)
Output: outputs/bank_measures_<PERIOD>.csv

Usage:
    python code/02_build_bank_measures.py                 # defaults to 2022Q4 / 12312022
    python code/02_build_bank_measures.py 2026Q2 06302026  # the "today" screen

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

    htm_loss             = htm_amortized_cost - htm_fair_value  (positive = loss)
    afs_loss             = afs_amortized_cost - afs_fair_value  (positive = loss)
    unreal_loss          = htm_loss + afs_loss
    unreal_loss_to_equity
    uninsured_dep_share  = uninsured_deposits / total_deposits

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
        "IDRSSD": "rssd_id",
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


def build_measures(folder: Path, period: str) -> pd.DataFrame:
    schedules = sorted({sched for _, sched in FIELDS.values()})
    raw = {s: read_schedule(folder, s, period) for s in schedules}

    out = read_por(folder, period)
    assert out["rssd_id"].is_unique

    for var, (codes, sched) in FIELDS.items():
        src = raw[sched]
        found = [c for c in codes if c in src.columns]
        if not found:
            raise KeyError(f"{var}: none of {codes} found in schedule {sched}")
        col = pd.DataFrame({"rssd_id": src["IDRSSD"],
                            var: pick_first_available(src, codes)})
        out = out.merge(col, on="rssd_id", how="left", validate="1:1")

    # Derived measures
    out["htm_loss"] = out["htm_amortized_cost"] - out["htm_fair_value"]
    out["afs_loss"] = out["afs_amortized_cost"] - out["afs_fair_value"]
    out["unreal_loss"] = out["htm_loss"].fillna(0) + out["afs_loss"].fillna(0)
    out["unreal_loss_to_equity"] = out["unreal_loss"] / out["total_equity"].where(out["total_equity"] > 0)
    out["uninsured_dep_share"] = out["uninsured_deposits"] / out["total_deposits"].where(out["total_deposits"] > 0)
    out["report_period"] = period

    assert out["rssd_id"].is_unique
    return out


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "2022Q4"
    period = sys.argv[2] if len(sys.argv) > 2 else "12312022"
    folder = ROOT / "inputs" / "call_reports" / label

    df = build_measures(folder, period)

    out_path = ROOT / "outputs" / f"bank_measures_{label}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print(f"Wrote {out_path.relative_to(ROOT)}: {len(df):,} banks")
    print(f"  with uninsured deposits reported: {df['uninsured_deposits'].notna().sum():,}")
    print(df[["uninsured_dep_share", "unreal_loss_to_equity"]].describe().round(3))


if __name__ == "__main__":
    main()
