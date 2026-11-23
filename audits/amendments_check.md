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

1. **Done 11/23: flag in the data.** Carry each bank's last-updated date into `outputs/bank_measures_2022Q4.csv` (`code/02` already reads the POR file). Add a holding-company flag, "any bank resubmitted after Mar 9, 2023", to `analysis_sample.csv`. That is a schema change, so it goes through Mithran.
2. **Done 11/23: robustness row** (`code/06d`, `specs_tried.md` #10; not estimable at v0, 2 banks). Rerun the main spec on banks not resubmitted after day 0, and log it in `specs_tried.md`. With ~59% of the ≥ $1B banks left, this is feasible at v1 scale.
3. **Look for as-filed values** for the largest banks: an archived copy of the FFIEC bulk file from early 2023, or the uninsured-deposit figures in each bank's 10-K for 2022, filed before or near the event. If none can be found, say so in the threats list.

Owner: Lucas. Target: the Nov 24 working groups.

## Follow-up 2026-11-23: as-filed uninsured deposits from the 10-Ks (instructor audit B3)

The bulk file keeps no older version, so we used the next-best as-filed source: each holding company's **10-K for 2022**. All 12 were filed Feb 14–28, 2023, before day 0. The figures were collected by hand from SEC EDGAR, with the URL and the exact wording for each, in `inputs/asfiled/uninsured_10k_2022q4.csv`. The README there explains the method.

**Not every 10-K figure can stand in for the call report.** The call-report item (RCON5597) covers U.S. offices at the bank level.
- **Same scope** (they say they use the regulatory or call-report method, or cover U.S. offices only): 8 holding companies.
- **Different scope** (firmwide, consolidated with intercompany adjustments, or including non-U.S. deposits): JPM, BAC, USB and WFC.

**Calibration.** CMA and SIVB never resubmitted and have same-scope 10-K figures. Both match the call report to within $0.1bn ($45.5bn vs $45.49bn, and $151.5bn vs $151.59bn), so for these banks the 10-K reproduces the original call report.

WFC never resubmitted either, but its consolidated 10-K figure is 29% below its call report. Different-scope figures therefore cannot show what a resubmission changed, so we do not use JPM's, BAC's or USB's.

**Result** (`outputs/asfiled_uninsured_comparison.csv`, `code/05b_asfiled_uninsured.py`). For the 6 resubmitted banks with same-scope 10-K figures, the current call report vs the 10-K:

| Bank | 10-K (Feb 2023), $bn | Current call report, $bn | Difference | Uninsured share: current → as filed |
|---|---|---|---|---|
| FITB | 69.4 | 88.3 | +27% | 0.522 → 0.410 |
| KEY | 67.1 | 75.8 | +13% | 0.519 → 0.460 |
| ZION | 38.0 (rounded) | 35.9 | −6% | 0.498 → 0.528 |
| PNC | 200.0 | 192.3 | −4% | 0.435 → 0.453 |
| TFC | 189.6 | 184.3 | −3% | 0.434 → 0.446 |
| WAL | 29.5 | 29.7 | +1% | 0.550 → 0.547 |

The resubmissions moved the uninsured measure a lot for two banks (FITB, KEY, both up) and little for the rest. The direction matches the FDIC letter for those two: banks were told to include deposits some had left out.

**Effect on the regression** (`code/06e`, `specs_tried.md` #11, `outputs/regression_asfiled_uninsured.csv`). The test reruns the main spec (11 banks) with the as-filed share where we have it, and the current share for JPM, BAC and USB:
- The uninsured-share slope moves from −0.15 (p = 0.89) to −0.40 (p = 0.77).
- The loss ratio and size barely change.
- At N = 11 neither version is evidence. In v1, `code/05b` and `06e` will need the 10-K figures for the full sample, or a rule for banks without one.
