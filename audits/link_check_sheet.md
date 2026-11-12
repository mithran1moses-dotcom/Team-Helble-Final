# Link table hand-check sheet

Closes open item 2 in `audits/01_self_audit.md` once every row is signed off.
**What is checked:** `inputs/links/bank_link_v0.csv`, 21 rows (ticker → holding company → bank subsidiary), as of 12/31/2022.

**Prepared:** 2026-11-11, by Lucas Koranda with Claude Code.
**Evidence files:** `audits/link_check_fdic.csv` and `audits/link_check_fdic_universe.csv`.
**Rerun:** `python dev/build_link_check_sheet.py`. This queries the FDIC BankFind API; no login is needed.

## What has already been checked automatically

Our link table was built from two sources: the NY Fed CRSP-FRB file and FFIEC NIC. The script compares each row with a **third, independent source**, the FDIC's own 12/31/2022 quarterly record for each bank:

- **Holder ✅:** the FDIC puts the bank under the same holding company RSSD that we do. For Zions, the FDIC shows no holding company, which matches our "the bank is its own holding company" row.
- **Assets ✅:** the FDIC's total assets for 12/31/2022 equal our call-report `total_assets` to the $1K.
- **Completeness:** every FDIC-insured bank that the FDIC places under one of our 12 holding companies on 12/31/2022 is listed and compared with our table (findings B and C below).

**Result:** 19 of 19 call-report filers match on holding company and total assets, and none of them is owned by another bank, so nothing is double counted. The 2 rows that don't file a call report are explained in finding A.

**Legend for the Checked column:** ✅ = confirmed by hand on NIC. FDIC ✅ = NIC couldn't show the 12/31/2022 record (usually because the bank has since closed), so the row rests on the FDIC's 12/31/2022 record in `audits/link_check_fdic.csv` instead.

## How to sign off a row (about 2 minutes each)

1. Open the row's **NIC** link. It opens the bank's profile as of today, so **change the page's date to 12/31/2022** before checking. If the link shows an error, go to <https://www.ffiec.gov/npw>, type the RSSD into the search box, and set the date there.
2. Confirm three things:
   - the legal name matches
   - the bank is **active** on 12/31/2022
   - in **Organization Hierarchy**, its *top* parent is the holding company in our table. Also note whether its *direct* parent is the holding company itself or another bank (this matters for finding C).
3. Tick ☐ → ☑ below and write anything odd in *Notes*.
4. When every row is done, fill `checked_by` (your name) and `checked_on` (the date) on each row of `inputs/links/bank_link_v0.csv`. From then on, `code/01b_build_link_table.py` refuses to overwrite the file.

## The 21 rows

| # | Ticker | bank_rssd | Bank (call report name) | Files call report? | FDIC holder ✅ | FDIC assets ✅ | Look up | Checked | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | BAC | 480228 | BANK OF AMERICA, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/480228) | ✅ | Direct parent: BAC NORTH AMERICA HOLDING COMPANY, 1379552 |
| 2 | BAC | 1443266 | BANK OF AMERICA CALIFORNIA, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/1443266) | ✅ | BAC NORTH AMERICA HOLDING COMPANY, 1379552 |
| 3 | CMA | 60143 | COMERICA BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/60143) | FDIC ✅ | NIC link fails: bank closed 2/1/2026 (merged into Fifth Third). FDIC 12/31/2022: holder Comerica Inc. (1199844), assets match, not owned by another bank. |
| 4 | CMA | 772446 | COMERICA BANK & TRUST, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/772446) | FDIC ✅ | NIC link fails: closed 2/1/2026 (merged into Fifth Third). FDIC 12/31/2022: holder Comerica Inc., assets match, parent bank = none, so owned directly by Comerica Inc.: **no double count** (finding C). |
| 5 | FITB | 723112 | FIFTH THIRD BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/723112) | ✅ | FIFTH THIRD FINANCIAL CORPORATION, 2990244|
| 6 | JPM | 651448 | JPMORGAN CHASE BANK, DEARBORN | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/651448) | FDIC ✅ | No financial data on NIC. FDIC 12/31/2022: holder JPMorgan Chase & Co. (1039502), assets match ($63M), not owned by another bank. |
| 7 | JPM | 852218 | JPMORGAN CHASE BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/852218) | ✅ | JPMORGAN CHASE & CO., 1039502|
| 8 | JPM | 2181444 | J.P. MORGAN TRUST COMPANY OF DELAWARE | **no** | — | — | [NIC](https://www.ffiec.gov/npw/Institution/Profile/2181444) | FDIC ✅ | No financial data on NIC. Not FDIC-insured, files no call report, dropped by `code/02`: adds nothing to any number (finding A). |
| 9 | KEY | 280110 | KEYBANK NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/280110) | ✅ | KEYCORP, 1068025|
| 10 | PNC | 817824 | PNC BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/817824) | ✅ | PNC BANCORP, INC., 1469314|
| 11 | SIVB | 802866 | SILICON VALLEY BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/802866) | FDIC ✅ | NIC link fails: bank closed 3/10/2023 (failed). FDIC 12/31/2022: holder SVB Financial Group (1031449), assets match, not owned by another bank. |
| 12 | TFC | 852320 | TRUIST BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/852320) | ✅ | TRUIST FINANCIAL CORPORATION, 1074156 |
| 13 | TFC | 2864774 | TRUIST DELAWARE TRUST COMPANY | **no** | — | — | [NIC](https://www.ffiec.gov/npw/Institution/Profile/2864774) | FDIC ✅ | NIC link fails. Not FDIC-insured, files no call report, dropped by `code/02`: adds nothing to any number (finding A). |
| 14 | USB | 212465 | MUFG UNION BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/212465) | FDIC ✅ | Profile opens but no hierarchy: bank closed 5/26/2023 (merged into U.S. Bank). FDIC 12/31/2022: holder U.S. Bancorp (1119794), assets match, not owned by another bank. |
| 15 | USB | 504713 | U.S. BANK NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/504713) | ✅ | U.S. BANCORP, 1119794 |
| 16 | WAL | 3138146 | WESTERN ALLIANCE BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/3138146) | ✅ | WESTERN ALLIANCE BANCORPORATION, 2349815 |
| 17 | WFC | 451965 | WELLS FARGO BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/451965) | ✅ | WFC HOLDINGS, LLC, 2741679 |
| 18 | WFC | 688079 | WELLS FARGO TRUST COMPANY, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/688079) | ✅ | Check its direct parent (see finding C). WFC HOLDINGS, LLC, 2741679 |
| 19 | WFC | 1225761 | WELLS FARGO NATIONAL BANK WEST | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/1225761) | ✅ | Check its direct parent (see finding C). WFC HOLDINGS, LLC, 2741679 |
| 20 | WFC | 2362458 | WELLS FARGO BANK SOUTH CENTRAL, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/2362458) | ✅ | Check its direct parent (see finding C). WFC HOLDINGS, LLC, 2741679|
| 21 | ZION | 276579 | ZIONS BANCORPORATION, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/276579) | ✅ | No hierarchy, as expected: Zions has no parent. FDIC 12/31/2022 also shows no holding company; assets match. |

## Findings (all resolved 2026-11-11)

**A. Rows 8 and 13 are not FDIC-insured, so they're correctly left out of the numbers.** RESOLVED.
J.P. Morgan Trust Company of Delaware and Truist Delaware Trust Company are not in the FDIC's data and file no call report. `code/02_build_bank_measures.py` prints and drops them, so they add nothing to any ratio. Their notes in `bank_link_v0.csv` used to say "insured trust company"; that is corrected.

**B. Five small FDIC-insured trust banks under our holding companies are not in our table.** RESOLVED: leaving them out is correct.
In the FDIC's 12/31/2022 data, each one is owned by a bank that *is* in our table (`PARCERT`, the parent bank's FDIC certificate). That parent's call report already includes them, so adding them would double count.

| Holding company | FDIC cert | Bank | Total assets, 12/31/2022 ($K) | Owned by (FDIC cert) |
|---|---|---|---|---|
| U.S. Bancorp | 34588 | U.S. Bank Trust Co NA | 1,493,108 | U.S. Bank NA (6548) |
| U.S. Bancorp | 57047 | U.S. Bank Trust National Assn | 719,653 | U.S. Bank NA (6548) |
| U.S. Bancorp | 34813 | U.S. Bank Trust NA SD | 134,668 | U.S. Bank NA (6548) |
| Wells Fargo & Co. | 34465 | Wells Fargo Delaware Trust Co NA | 233,670 | Wells Fargo Bank NA (3511) |
| KeyCorp | 59069 | Key National Trust Co of Delaware | 6,481 | KeyBank NA (17534) |

**C. Possible double count when the parent bank has no NIC record (Comerica).** RESOLVED: no double count.
The worry was that Comerica Bank & Trust (row 4) might be owned by Comerica Bank, which `code/01b` can't recognize as a bank. The FDIC's 12/31/2022 record shows it has no parent bank (`PARCERT` = 0); it is owned directly by Comerica Inc. The same holds for all 19 kept banks, and `dev/build_link_check_sheet.py` now asserts it.
**Still worth fixing for v1:** `code/01b` should treat any entity that files a call report as a bank, even when NIC has no record for it, so this can't happen silently with ~100 banks.

**What we learned about NIC:** profile links fail, or show no hierarchy, for institutions that have since closed (SVB, MUFG Union Bank, both Comerica banks). For those rows, the FDIC's quarterly record for 12/31/2022 is the as-of-date evidence.

## Sign-off

| Reviewer | Date | Rows checked | Findings A/B/C resolved? |
|---|---|---|---|
| | | /21 | |
