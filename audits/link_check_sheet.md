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

**Result:** 19 of 19 call-report filers match on both holding company and total assets. The 2 rows that don't file a call report are explained in finding A.

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
| 1 | BAC | 480228 | BANK OF AMERICA, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/480228) | ☐ | |
| 2 | BAC | 1443266 | BANK OF AMERICA CALIFORNIA, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/1443266) | ☐ | |
| 3 | CMA | 60143 | COMERICA BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/60143) | ☐ | No NIC record in our download; the name comes from the call report. See finding C. |
| 4 | CMA | 772446 | COMERICA BANK & TRUST, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/772446) | ☐ | **See finding C:** is its direct parent Comerica Inc. or Comerica Bank? |
| 5 | FITB | 723112 | FIFTH THIRD BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/723112) | ☐ | |
| 6 | JPM | 651448 | JPMORGAN CHASE BANK, DEARBORN | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/651448) | ☐ | Small ($63M). Check its direct parent: JPMorgan Chase & Co. or Chase Bank NA? |
| 7 | JPM | 852218 | JPMORGAN CHASE BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/852218) | ☐ | |
| 8 | JPM | 2181444 | J.P. MORGAN TRUST COMPANY OF DELAWARE | **no** | — | — | [NIC](https://www.ffiec.gov/npw/Institution/Profile/2181444) | ☐ | See finding A. |
| 9 | KEY | 280110 | KEYBANK NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/280110) | ☐ | |
| 10 | PNC | 817824 | PNC BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/817824) | ☐ | |
| 11 | SIVB | 802866 | SILICON VALLEY BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/802866) | ☐ | Failed 3/10/2023, so it is inactive today but must show **active** on 12/31/2022. |
| 12 | TFC | 852320 | TRUIST BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/852320) | ☐ | |
| 13 | TFC | 2864774 | TRUIST DELAWARE TRUST COMPANY | **no** | — | — | [NIC](https://www.ffiec.gov/npw/Institution/Profile/2864774) | ☐ | See finding A. |
| 14 | USB | 212465 | MUFG UNION BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/212465) | ☐ | No NIC record in our download. Acquired by U.S. Bancorp 12/1/2022 and merged into U.S. Bank 5/26/2023, so it must be included on 12/31/2022. |
| 15 | USB | 504713 | U.S. BANK NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/504713) | ☐ | |
| 16 | WAL | 3138146 | WESTERN ALLIANCE BANK | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/3138146) | ☐ | |
| 17 | WFC | 451965 | WELLS FARGO BANK, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/451965) | ☐ | |
| 18 | WFC | 688079 | WELLS FARGO TRUST COMPANY, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/688079) | ☐ | Check its direct parent (see finding C). |
| 19 | WFC | 1225761 | WELLS FARGO NATIONAL BANK WEST | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/1225761) | ☐ | Check its direct parent (see finding C). |
| 20 | WFC | 2362458 | WELLS FARGO BANK SOUTH CENTRAL, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/2362458) | ☐ | Check its direct parent (see finding C). |
| 21 | ZION | 276579 | ZIONS BANCORPORATION, NATIONAL ASSOCIATION | yes | ✅ | ✅ | [NIC](https://www.ffiec.gov/npw/Institution/Profile/276579) | ☐ | The bank is the listed company (no holding company); the FDIC agrees. |

## Findings to resolve

**A. Rows 8 and 13 are not FDIC-insured, so they're correctly left out of the numbers.**
J.P. Morgan Trust Company of Delaware and Truist Delaware Trust Company are not in the FDIC's data and file no call report. `code/02_build_bank_measures.py` already prints and drops them, so they add nothing to any ratio. Their note in `bank_link_v0.csv` says "insured trust company", which is wrong; change it to "non-insured trust company, files no call report".

**B. Five small FDIC-insured trust banks sit under our holding companies but aren't in our table.**

| Holding company | FDIC cert | Bank | Total assets, 12/31/2022 ($K) |
|---|---|---|---|
| U.S. Bancorp | 34588 | U.S. Bank Trust Co NA | 1,493,108 |
| U.S. Bancorp | 57047 | U.S. Bank Trust National Assn | 719,653 |
| U.S. Bancorp | 34813 | U.S. Bank Trust NA SD | 134,668 |
| Wells Fargo & Co. | 34465 | Wells Fargo Delaware Trust Co NA | 233,670 |
| KeyCorp | 59069 | Key National Trust Co of Delaware | 6,481 |

The link builder (`code/01b`) deliberately drops a bank whose direct parent is another bank, because the parent's call report already includes it. If these five are owned by U.S. Bank NA, Wells Fargo Bank NA and KeyBank NA, leaving them out is **correct**. If any is owned directly by the holding company, we're missing it.
**To check:** look up each one on NIC as of 12/31/2022 and note its direct parent.
**How much it matters:** very little. Even all three U.S. Bank trust companies together (about $2.3B) are 0.3% of USB's $689.6B.

**C. Possible double count when the parent bank has no NIC record (Comerica, and in principle USB).**
`code/01b` recognizes "parent is a bank" only for entities that appear in the NIC attribute files. Comerica Bank (60143) and MUFG Union Bank (212465) are missing from those files. So if one of them owns another bank, the builder would keep that bank *as well as* its parent, and count it twice.
- **Comerica, the case to check:** Comerica Bank & Trust (row 4, $76M) is kept. If its direct parent is **Comerica Bank** and not Comerica Inc., its assets are already inside Comerica Bank's call report and are double-counted. That would be $76M of $85.6B (0.09%), so it doesn't change any result, but it is a real merge error an auditor could find.
- **If it is double-counted:** delete row 4 from `bank_link_v0.csv` (with a note saying why), then rerun `python run_all.py`.
- **Fix for v1 regardless:** in `code/01b`, treat any entity that files a call report (it has an FDIC cert in the call-report filer list) as a bank, even when NIC has no attribute record for it.

## Sign-off

| Reviewer | Date | Rows checked | Findings A/B/C resolved? |
|---|---|---|---|
| | | /21 | |
