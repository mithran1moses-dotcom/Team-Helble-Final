# Check: call report field codes (MDRM), as of 12/31/2022

Closes open item 3 in `audits/01_self_audit.md`.

**Prepared:** 2026-11-11, by Lucas Koranda with Claude Code.
**Reviewed by a person:** _name, date_ (read this file, rerun the script, and confirm the table matches).

**Source:** Federal Reserve Micro Data Reference Manual (MDRM), <https://www.federalreserve.gov/apps/mdrm/pdf/MDRM.zip>, downloaded 2026-11-11.
**Rerun:** `python dev/check_mdrm_codes.py`. This downloads the dictionary into `temp/`, which is git-ignored.

## Result: all 14 codes check out

Every code used in `code/02_build_bank_measures.py` (`FIELDS`) is in force on 12/31/2022, under the name we assumed.

| Variable | Codes (preferred first) | MDRM item name | Forms carrying it (12/31/2022) |
|---|---|---|---|
| `total_assets` | RCFD2170, RCON2170 | TOTAL ASSETS | RCFD: 031 · RCON: 031, 041, 051 |
| `total_equity` | RCFD3210, RCON3210 | TOTAL EQUITY CAPITAL (the call report labels it "Total bank equity capital", RC item 27.a) | RCFD: 031 · RCON: 041, 051 |
| `total_deposits` | RCON2200 | TOTAL DEPOSITS (domestic offices) | 031, 041, 051 |
| `uninsured_deposits` | RCON5597 | ESTIMATED AMOUNT OF UNINSURED ASSESSABLE DEPOSITS IN DOMESTIC OFFICES… (RC-O Memo 2) | 031, 041 (see note 2) |
| `htm_amortized_cost` | RCFD1754, RCON1754 | HELD-TO-MATURITY SECURITIES; TOTAL | RCFD: 031 · RCON: 031, 041, 051 |
| `htm_fair_value` | RCFD1771, RCON1771 | TOTAL FAIR VALUE OF HELD-TO-MATURITY SECURITIES | RCFD: 031 · RCON: 041, 051 |
| `afs_amortized_cost` | RCFD1772, RCON1772 | TOTAL AMORTIZED COST OF AVAILABLE-FOR-SALE SECURITIES | RCFD: 031 · RCON: 041, 051 |
| `afs_fair_value` | RCFD1773, RCON1773 | Available-for-sale debt securities (from Schedule RC-B; column D) | RCFD: 031 · RCON: 031, 041, 051 |

## Notes

1. **The RCFD-then-RCON rule is right.** 031 filers (banks with foreign offices) report the consolidated RCFD versions. For 3210, 1771 and 1772 there is no RCON version on the 031 form at all. 041 and 051 filers report only RCON. So taking RCFD when present and RCON otherwise gives every bank its whole-bank number.
2. **RCON5597 on the 051 form.** MDRM does not list FFIEC 051 for RCON5597, but our 12/31/2022 data shows 051 filers do report it. In `outputs/bank_measures_2022Q4.csv`, 307 of 363 051 filers with $1–5B in assets have a value. This looks like a gap in MDRM's form list, not in the data. It matters for v1, where many small banks are 051 filers.
3. **Uninsured deposits are reported bank by bank, unconsolidated.** The MDRM description says Memo 2 is completed "on an unconsolidated single FDIC certificate number basis by banks with $1 billion or more in total assets." Summing subsidiaries to the holding company therefore does not double-count.
4. **The two halves of the uninsured share are both domestic.** RCON5597 covers domestic offices, and so does RCON2200. That's consistent, including for the 031 filers (JPM, BAC, WFC and others) whose total assets and equity are consolidated.
5. **Who reports uninsured deposits, 12/31/2022** (all 4,756 call report filers, from `outputs/bank_measures_2022Q4.csv`):

| Total assets | Filers | Reporting RCON5597 |
|---|---|---|
| < $1B | 3,770 | 16 |
| $1–5B | 713 | 634 |
| > $5B | 273 | 273 |

   Every bank over $5B reports it. Some banks between $1B and $5B don't. One plausible reason is that the $1B test may be based on assets at an earlier report date, so banks that recently crossed $1B don't report yet. **Check this before v1**, because those banks will have a missing `uninsured_dep_share`.

## What this check does not cover

- It confirms the **codes**, not our **numbers**. The spot check that SVB's HTM loss ($15.2B), BAC's ($108.6B) and WFC's ($41.6B) match widely reported figures is still the evidence for the values.
- It does not fix the AFS-to-HTM transfer issue (open item 4). The codes are right, but HTM amortized cost minus fair value leaves out losses that were locked in when securities were moved from AFS to HTM.
