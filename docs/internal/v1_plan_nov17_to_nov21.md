# v1 plan — four people, Tue Nov 17 → Sat Nov 21

Built from the v0 plan (`v0_plan_nov3_to_nov9.docx`), updated for what actually happened in v0 (GitHub history through Nov 16), the v1 requirements in `docs/course/`, and the instructor's Checkpoint 2 audit (`audits/03_instructor_audit.md` on branch `instructor-audit-cp2`). `DECISIONS.md` in the repo root still overrides this file.

**Due Sat Nov 21:** v1 full-sample results **and** `audits/04_audit_response.md` answering the instructor audit (findings A1–A4). The course page still says Thu Nov 19 for v1; `DECISIONS.md` and the instructor audit both say Sat Nov 21. Working groups on audit findings: Tue Nov 24. Presentations: Dec 1 / Dec 3.

## What changed since the v0 plan

v0 shipped, but not the way the plan said. The v1 plan starts from what is in the repo, not from the v0 plan.

| v0 plan said | What happened (GitHub) | What it means for v1 |
|---|---|---|
| v0 due Mon Nov 9, proposal Thu Nov 12 | Both moved to Sat Nov 14 (HW8). Pipeline merged Nov 9 (PR #2), v0 + proposal Nov 14 (PR #5) | v1 is Sat Nov 21, one week after v0, not ten days |
| A (Mithran) = dashboard only; B (Lucas) = link table + call reports; C (Marc) = returns | Mithran built the whole pipeline (link table, call reports, CRSP returns, event study, merge, regression) and the dashboard with Claude Code, Nov 7–9. Lucas hand-checked all 21 link rows, verified the MDRM codes, tidied the repo, restructured the self-audit, converted the proposal and did the first Streamlit deploy (Nov 11–14). No commits from Marc or Riley are on GitHub (the `Marc-returns` branch holds only Lucas's upload) | Ownership was lopsided and checklist item 10 ("every teammate can explain every step") is marked *Not yet*. v1 hands each person one pipeline stage to own, rerun and explain |
| Toy CSV first, dashboard built against it | Toy data skipped (decided 11/7); dashboard built on the real 12-row file | No toy step in v1. The dashboard switches to the v1 file once it exists |
| yfinance prices | Switched to CRSP via WRDS (11/9), matched by PERMNO via PERMCO; no-trade days dropped | Every v1 return comes from CRSP. **Anyone rerunning steps 03–04 needs a WRDS login** |
| Notebooks (`01_download_callreports.ipynb` …), `data/interim/` | Plain `.py` scripts in `code/` (01a–06b), `run_all.py`, `inputs/` and `outputs/` | v1 extends the existing scripts; no new notebooks |
| `docs/final_row.md` spec file; CAR window Mar 9–13, estimation to late Feb | Spec lives in `README.md` + `DECISIONS.md`. Column is `car_0_2` (days 0 to +2, Mar 9–13); estimation window = 2022 | Column names are frozen. Renames still go through Mithran (schema owner) |
| Hand link table for 12 banks, matched by name | Same, via the NY Fed CRSP-FRB file + NIC; v0 matched holding companies **by name** because the NY Fed file has no tickers | ~100 banks can't be name-matched by hand. v1 starts from CRSP and joins on **PERMCO**, then hand-checks a sample |
| "Robustness specs deliberately skipped" | One robustness run done (without ZION, `specs_tried.md` #5) | v1 adds the robustness rows the audits ask for |

## v1 scope

**Sample: every listed U.S. bank that passes filters written down before the regression runs** (Seed 6 MVP: about 100 banks, one event). This answers self-audit finding 20 (v0 sample picked knowing the outcome).

**Proposed filters, to agree on Tuesday and log in `DECISIONS.md` + `specs_tried.md` before anything runs:**

1. In the NY Fed CRSP-FRB link file on 2022-12-31 (bank holding company or commercial bank with an RSSD).
2. Common stock in CRSP (share code 10 or 11) trading on 2023-03-08, the day before day 0.
3. Files a 12/31/2022 call report through at least one bank subsidiary.
4. Total assets ≥ $1bn (the RCON5597 uninsured-deposit reporting cutoff).
5. At least 200 trading days with a real trade in the 2022 estimation window.
6. A liquidity floor (e.g. median 2022 daily dollar volume, cutoff picked before looking at CARs). This is the Seed 6 auditors' "small illiquid banks" point.
7. **Failed-bank rule (instructor A1):** banks that failed inside the event window are out of the main spec and reported separately: SIVB (Mar 10) and SBNY (Mar 12). FRC failed May 1, outside the window, so by this rule it stays in. **Team to decide** whether to also drop FRC; whatever we pick, log it before running.

**v1 is not the final answer either.** It is the full-sample result plus the fixes the instructor asked for. The First Republic second event stays a stretch goal.

## The tasks and who owns them

Letters match the v0 plan. Each owner reruns their stage from scratch on their own machine and walks the team through it before Saturday (checklist item 10).

| # | Task | File | Owner | Answers |
|---|---|---|---|---|
| 1 | Agree on filters, failed-bank rule and the spec list; write them down **before** any v1 regression | `DECISIONS.md`, `specs_tried.md` | All, Tue; D writes | Finding 20, checklist 6 |
| 2 | v1 universe: CRSP banks on 2023-03-08 → PERMCO → NY Fed link → RSSD → bank subsidiaries; report the match rate at each step | `code/01b_build_link_table.py` (extend) → `inputs/links/bank_link_v1.csv` | A | Seed 6 "ID link quality" |
| 3 | Hand-check a random sample of ~20 v1 link rows on NIC/FDIC, same sheet format as v0 | `audits/link_check_sheet.md` | B | Checklist 8 |
| 4 | Script the call-report download (instructor gave the form fields); pull 12/31/2022 and the latest quarter (9/30/2026) | `code/00_download_call_reports.py` | B | Instructor A4 |
| 5 | Run measures for the v1 universe (2022Q4) and the latest quarter | `code/02_build_bank_measures.py` → `outputs/bhc_measures_2022Q4.csv`, `outputs/bhc_measures_latest.csv` | A runs, B checks | Instructor A3 |
| 6 | Amendments check: POR "last updated" dates for every filer; flag any amended after Mar 9, 2023, especially after the FDIC letter of Jul 24, 2023 | `audits/` note + flag column | B | Finding 10, PR #6 |
| 7 | Compare summed subsidiaries to FR Y-9C equity/assets for the 12 v0 banks; uninsured share over reporting subsidiaries only | `audits/` note; robustness row | B | Findings 11, 21 |
| 8 | CRSP pull for the v1 universe + SPY; event study for every bank | `code/03_download_crsp.py`, `code/04_event_study.py` → `outputs/car_0_2.csv` | C (needs WRDS) | — |
| 9 | CAR hand check: recompute KEY's `car_0_2` in a spreadsheet from its CRSP rows and SPY; cite the instructor's yfinance match too | `audits/car_hand_check.md` | C | Finding 9, checklist 8 |
| 10 | Robustness returns: market model with a bank index next to SPY; longer window 0 to +4 | new rows in `specs_tried.md` | C | Finding 12 |
| 11 | Merge, assert unique `bhc_rssd`, `validate=` on every merge, assert the N the filters predict | `code/05_build_analysis_sample.py` | A + C | Checklist 3 |
| 12 | Regression: failed banks out of the main spec (with-SIVB row kept as robustness), `cov_type="HC3", use_t=True`, effects in CAR points per 1 SD of each measure | `code/06_regression.py`, `06b` | A + C | Instructor A1, A2; checklist 7 |
| 13 | Dashboard: v1 results; fragility screen points at the latest quarter with its report date shown; note on CMA (merged into FITB Feb 2026); t-based p-values | `app.py` | A | Instructor A3, PR #6 §3 |
| 14 | Pin package versions (`pip freeze`); let `run_all.py --download` run past 01b | `requirements.txt`, `run_all.py` | D | Instructor A4, finding 22 |
| 15 | Merge PR #6 (external findings); swap trade-press links for the FDIC Jul 24, 2023 letter and Comerica's 8-K; sign the "reviewed by a person" line | `audits/02_external_findings.md` | D | PR #6 |
| 16 | Fill the hypothesis section of the proposal, written by us, not an agent | `PROPOSAL.md` | D, with the team | Instructor A3, finding 3 |
| 17 | Audit response: each instructor finding marked fixed (commit), disputed (why) or disclosed (where) | `audits/04_audit_response.md` | D | Instructor deadline |
| 18 | Rerun the Skeptical review prompt on v1; new self-audit with the 10-point checklist | `audits/05_self_audit_v1.md` | D | Course standard |
| 19 | README, STATUS, threats to validity; PR reviews | — | D | Checklist 9 |

**A — Mithran: universe, merge, regression, dashboard.** Schema owner. The v1 universe is the critical path, as the link table was in v0.
**B — Lucas: fundamentals and their checks.** Call-report download script, latest quarter, link sample check, amendments, Y-9C comparison. Builds on the v0 link and MDRM checks he already did.
**C — Marc: returns.** His v0 role, now on CRSP: full-universe pull, event study, CAR hand check, return robustness. Needs a WRDS login on day 1.
**D — Riley: audit response, proposal, repo.** As in v0: writes no pipeline code, reviews every PR, owns every document the instructor reads first.

## Schedule

| | A — Mithran (universe / merge / dashboard) | B — Lucas (fundamentals) | C — Marc (returns) | D — Riley (audit / proposal / repo) |
|---|---|---|---|---|
| **Tue 11/17** | Filters meeting; start v1 universe from CRSP + NY Fed link | Filters meeting; call-report download script | Filters meeting; get WRDS working, rerun v0 `03`–`04` and match the committed CARs | Filters meeting; write filters + spec list into `DECISIONS.md` and `specs_tried.md`; merge PR #6 |
| **Wed 11/18** | Link table v1 with match rates; hand list to B and C | Pull 2022Q4 + latest quarter; amendments check | CAR hand check for KEY | Pin requirements; fix `run_all.py --download`; start `04_audit_response.md` |
| **Thu 11/19** | Run `02` on the v1 universe and latest quarter | Hand-check ~20 link rows; Y-9C comparison | CRSP pull + event study for the v1 universe | Proposal hypothesis draft with the team; replace PR #6 sources |
| **Fri 11/20** | Merge with C → `analysis_sample.csv` | Uninsured-share robustness (finding 21) | ← merge with A; HC3 regression, failed-bank rule, magnitudes | Skeptical review rerun on Friday's repo |
| **Sat 11/21** | Dashboard on v1 + latest-quarter screen; final `run_all.py` | Walk the team through `02` | Robustness rows (bank index, 0 to +4, with SIVB); walk the team through `03`–`04` | Finish `04_audit_response.md`, v1 self-audit, README/STATUS; v1 PR |

**Friday's milestone: `analysis_sample.csv` with every bank that passes the filters, the N asserted, and the filters committed before the regression ran.** Everything else is built around that file.

## The one coordination point

Tuesday, all four agree on the filters, the failed-bank rule and the list of specs to run, and D commits them before anyone runs a v1 regression. In v0 the risk was column names; in v1 it is choosing the sample or the spec after seeing the results. The column names from v0 do not change.

## Self-audit contents for v1

Write it as attacks on our own repo:

- **Sample selection:** filters logged before the run; how many banks each filter drops; failed banks reported separately
- **Link quality at scale:** match rate at each step, hand-checked sample, banks lost and why
- **Look-ahead through amendments:** how many filers amended 2022Q4 after Mar 9, 2023, and what we did about them
- **Illiquid banks:** liquidity filter and a result with and without it
- **Holding company vs. subsidiaries:** Y-9C gaps; intercompany deposits in multi-subsidiary parents
- **Inference:** HC3 with t p-values; magnitudes per SD, not stars
- **"Today" screen:** latest-quarter date shown; banks that merged since 2023 (CMA)
- **Specs tried:** every row, including dropped ones

## Deliberately skipped

First Republic as a second event, FR Y-9C as the main data source, LLM anything, new chart types. Stretch only if Friday's milestone is met early.

## Risk

**A is the critical path.** Going from 12 hand-named banks to ~100 joined by PERMCO is where things break: holding companies with several share classes (several PERMNOs per PERMCO), banks listed after 2022, and the NY Fed link file ending at 2024-09-30, which won't cover banks listed since for the "today" screen. If the universe isn't ready by Wednesday night, B pairs with A and the amendments/Y-9C checks move to the Nov 24 working groups (disclosed as open in the audit response).

**C depends on WRDS.** If Marc's WRDS access isn't working by Tuesday night, A runs the CRSP pull and C takes the hand check and robustness only.

**D's work has a hard deadline of its own:** the instructor audit response is due Saturday whatever happens to the full-sample run. Anything not fixed is listed as disclosed, with a plan.
