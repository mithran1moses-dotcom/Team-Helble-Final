# Amendments check: were our 12/31/2022 call reports changed after the event?

Run 2026-11-21 by Lucas Koranda with Claude Code. Answers self-audit finding 10, v1 plan task 6, and the vintage point in instructor audit A4.

Rerun with `python dev/check_amendments.py`. The numbers below come from `audits/amendments_check.csv` (one row per link-table bank) and `audits/amendments_check_summary.csv` (counts).

## The question

The FFIEC bulk file we use holds the **current** version of each bank's 12/31/2022 call report ("CDR data as of 2026-09-15"). A bank can resubmit (amend) a report years later. If it did so after **Mar 9, 2023** (day 0), our fragility measures may differ from what investors could see during the event. That would be look-ahead.

The date that matters most is **Jul 24, 2023**. On that day the FDIC told banks to correct how they report estimated uninsured deposits (RCON5597), and uninsured deposits are one of our two main measures.

## What the data can and cannot tell us

The Panel of Reporters file (`FFIEC CDR Call Bulk POR 12312022.txt`) gives one date per bank: "Last Date/Time Submission Updated On".
- **It can tell us** whether a bank's report has been resubmitted since a given date.
- **It cannot tell us** which items changed, or by how much. It keeps only the latest date, and the bulk file keeps only the latest values. A resubmission might change our variables, or only unrelated items.

So a date after Mar 9, 2023 means "may differ from what the market saw", not "did change".

## Results

**Our 12 holding companies: 9 have a report resubmitted after day 0.** In every case it is the main bank (85–100% of the holding company's assets), and every one came after the FDIC letter.

| Holding company | Bank resubmitted after Mar 9, 2023 | Last updated | Share of holding-company assets |
|---|---|---|---|
| BAC | Bank of America, N.A. | 2025-09-23 | 99.3% |
| FITB | Fifth Third Bank, N.A. | 2023-12-06 | 100% |
| JPM | JPMorgan Chase Bank, N.A. | 2024-08-30 | 100% |
| KEY | KeyBank N.A. | 2024-06-24 | 100% |
| PNC | PNC Bank, N.A. | 2024-09-06 | 100% |
| TFC | Truist Bank | 2025-09-18 | 100% |
| USB | U.S. Bank N.A. | 2024-06-20 | 84.9% |
| WAL | Western Alliance Bank | 2023-08-18 | 100% |
| ZION | Zions Bancorporation, N.A. | 2026-03-30 | 100% |

**Not resubmitted after day 0:** SIVB (last updated 2023-02-16), CMA (2023-02-22) and WFC (2023-02-03), plus every small subsidiary bank. Their numbers are what the market could see.

**All filers** (`audits/amendments_check_summary.csv`):

| Group | Banks | Resubmitted after Mar 9, 2023 | After Jul 24, 2023 |
|---|---|---|---|
| Our filing banks | 19 | 9 (47%) | 9 |
| Our holding companies (any bank) | 12 | 9 (75%) | 9 |
| All filers | 4,756 | 973 (20%) | 441 |
| All filers with assets ≥ $1B | 986 | 407 (41%) | 269 |

The last row matters most for v1. The full sample will come from banks of this size, so roughly 4 in 10 of them will have a report resubmitted after the event.

## What it means

- **Finding 10 is real, not just plausible.** For 9 of our 12 holding companies we use a version of the 12/31/2022 report that did not exist on Mar 9, 2023.
- **We don't know how much the numbers moved.** The bulk file has no older version to compare with.
- **Uninsured deposits are the most likely to have changed.** Every resubmission came after the FDIC letter about that item, and the external findings in PR #6 report restatements of Q4 2022 uninsured deposits.
- **Losses on securities are less likely to have changed**, since they rest on year-end fair values that banks also report in their audited 10-Ks. That is a guess, not something we checked.
- **No fix is possible at v0.** Dropping the 9 banks would leave 2 non-failed banks (CMA, WFC), too few for a regression.

## Plan (v1)

1. **Flag in the data.** Carry each bank's last-updated date into `outputs/bank_measures_2022Q4.csv` (`code/02` already reads the POR file). Add a holding-company flag, "any bank resubmitted after Mar 9, 2023", to `analysis_sample.csv`. That is a schema change, so it goes through Mithran.
2. **Robustness row.** Rerun the main spec on banks not resubmitted after day 0, and log it in `specs_tried.md`. With ~59% of the ≥ $1B banks left, this is feasible at v1 scale.
3. **Look for as-filed values** for the largest banks: an archived copy of the FFIEC bulk file from early 2023, or the uninsured-deposit figures in each bank's 10-K for 2022, filed before or near the event. If none can be found, say so in the threats list.

Owner: Lucas. Target: the Nov 24 working groups.
