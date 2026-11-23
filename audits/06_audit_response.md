# Response to the instructor audit (Checkpoint 3)

Replies to `audits/05_instructor_audit.md` (audited commit `61ed6c7`; PR #10, checklist in issue #11). Each finding is marked **fixed** (with the commit), **disputed** (with the reason), or **open / disclosed** (where it is written down, and the plan).

Draft started 2026-11-23 by Lucas Koranda with Claude Code, on branch `v0-pipeline`. Riley (D in the v1 plan) owns this file and finishes it.

| ID | Finding | Status | Where |
|---|---|---|---|
| B1 | v1 is not on the full sample | **Open** | below |
| B2 | Live dashboard deploys from `main`; the work is not on `main` | **Open**: needs PR #9 merged | below |
| B3 | Call reports include resubmissions made after the event | **Partly fixed**: flag and robustness row in commit `1bb2c48`; as-filed values still to find | below |
| B4 | The CAR hand check is still the auditor's | **Open** | below |
| CP2 A3 | Proposal hypothesis; "today" screen | Screen fixed (`9932a41`); **hypothesis open** | below |

## B1 · Open: v1 is not on the full sample

We agree: the repo is still the 12 v0 banks.

**Plan** (`docs/internal/v1_plan_nov17_to_nov21.md`):
1. Write the sample filters into `DECISIONS.md` and `specs_tried.md` before running anything.
2. Build the universe: CRSP banks trading on 2023-03-08 → PERMCO → NY Fed link → RSSD → bank subsidiaries, reporting the match rate at each step.
3. Hand-check a random sample of about 20 links.
4. Pull CRSP for the universe and run the event study.
5. Rerun `02`, `05`–`06d`, with the final N and every exclusion counted.

**Blocked on:** a WRDS login (steps 2 and 4) and the FFIEC NIC files (step 2, a manual download). Neither is on the machine where this draft was written.

**Owners:** Mithran (universe, merge, regression), Marc (CRSP, event study), Lucas (link checks).

**Target:** before Dec 1.

## B2 · Open: merge the work into `main`

The A1–A4 fixes, the 2026Q3 screen and the B3 work exist only on PR #9 (`v0-pipeline`).

**Plan:**
1. Review and merge PR #9, then PR #6.
2. In the Streamlit Cloud settings, set Python 3.11 (the version `requirements.txt` was tested on).
3. Reload https://team-helble-final.streamlit.app/ and check that the Analysis tab says 11 banks and HC3.

**Owner:** the team (review), Mithran (deploy).

## B3 · Partly fixed: resubmitted call reports are flagged, with a robustness row

**What we changed (commit `1bb2c48`):**
- **The date, carried into the data.** `code/02` keeps each bank's "Last Date/Time Submission Updated On" from the POR file:
  - `last_updated` in `outputs/bank_measures_*.csv`;
  - `last_updated_max`, the latest date among a holding company's banks, in `outputs/bhc_measures_*.csv`.
  - Every bank must have a date (asserted).
- **The flag.** `code/05` adds `resubmitted_after_event` to `outputs/analysis_sample.csv`. It is True for 9 of 12 holding companies (asserted), matching `audits/amendments_check.md`. Only CMA, SIVB and WFC are False.
- **Tested on fake data.** The fake call reports now have last-updated dates, and `dev/check_fake_bhc_measures.py` checks `last_updated_max` against hand-worked answers.
- **The robustness row.** `code/06d_robustness_not_resubmitted.py` reruns the main spec on holding companies not resubmitted after Mar 9, 2023. It is logged as `specs_tried.md` #10 → `outputs/regression_not_resubmitted.*`. The rule was written in `DECISIONS.md` ("Resubmitted call reports") before the run.
- **Nothing else moved.** Every existing output column is unchanged (only new columns were added), and the regression CSVs are identical.

**Result at v0:** not estimable. After dropping SIVB (failed) and the 9 resubmitted banks, only CMA and WFC are left, fewer than the 4 coefficients. `outputs/regression_not_resubmitted.csv` says so instead of reporting a number. In v1, about 59% of filers with assets ≥ $1B were not resubmitted (`audits/amendments_check_summary.csv`), so the row will run. The README will then say whether the main coefficients move.

**Still open: an as-filed uninsured measure.**
- **Plan:** collect estimated uninsured deposits as of 12/31/2022 from each affected bank's 10-K for 2022, filed in Feb–Mar 2023. Or check whether the FR Y-9C has an equivalent item. Then rerun the main spec with that measure.
- **Starting point:** the 9 v0 holding companies, so we can see how far the resubmitted values moved.
- **Owner:** Lucas. **Target:** before Dec 1.

## B4 · Open: our own CAR hand check

**Plan:**
1. Recompute KEY's `car_0_2` in a spreadsheet from its CRSP daily returns and SPY: market model on 2022, then the abnormal returns on Mar 9, 10 and 13, 2023.
2. Do the same for one small bank once the v1 universe exists.
3. Record the inputs, the formula and both values in `audits/car_hand_check.md`, matching `outputs/car_0_2.csv` to 4 decimals.

**Blocked on:** WRDS access (the CRSP rows are git-ignored under the license).

**Owner:** Marc.

## CP2 A3 · Screen fixed; hypothesis open

- **Screen: fixed** (commit `9932a41`). The instructor confirmed it.
- **Hypothesis: open.** `PROPOSAL.md:23–25` ("TEAM HYPOTHESIS AND THOUGHTS") is still motivation, not a testable hypothesis. The team writes it, not an agent, as HW8 asks. It should state the expected signs of the two slopes in the main spec, which are negative for uninsured share and for the loss ratio, and what result would count against them.
- **Owner:** Riley, with the team.
