# Team Helble — v0 Decisions & Changes

Running log of decisions and changes for the Bank Fragility project (Seed 6). Owner of schema: Mithran (A).

## Corrected deadlines (from course instructions, updated Nov 5)

- **v0 checkpoint + proposal (HW8): Sat Nov 14.** Not Mon Nov 9 / Thu Nov 12 as in the original plan doc.
- **v1 full-sample results: Sat Nov 21.** Not Nov 19.
- Working groups to fix audit findings: Tue Nov 24.
- Presentations: Dec 1 / Dec 3.
- v0 must include: whole pipeline on a small sample, dashboard skeleton, and `audits/01_self_audit.md`. The proposal is written from the working v0.

## Event window

- **No course requirement** on the window. Seed 6 only says "CAR around March 2023".
- **Decided: main window March 9–13, 2023 = trading days 0 to +2, day 0 = March 9.**
- Column name: `car_0_2` (replaces the README's `car_0_5`).
- Reason: captures the run, seizure, Signature closure and backstop; avoids the March 15 Credit Suisse shock; less noise.
- Longer window (e.g. 0 to +4) can be a robustness check, logged in `specs_tried.md`.
- Decided for v0: estimation window ends before 2023 (as in the README). Can revisit for v1.

## Sample

- **Decided: 12 banks for v0:** JPM, BAC, WFC, USB, PNC, TFC, FITB, KEY, ZION, WAL, CMA, SIVB.
- The README says \~100 banks; that is the v1 target, not v0. PACW is not in v0.
- **Unit of observation: bank holding company.** Collapse subsidiaries: sum dollar amounts across each holding company's bank subsidiaries first, then compute ratios.

## Loss ratio

- **Decided: main measure = (HTM loss + AFS loss) / (total equity + AFS loss).** Follows Jiang, Matvos, Piskorski & Seru (2023).
- AFS losses are added back to the denominator because they are already deducted from book equity.
- Robustness: HTM loss only. Column names: main = `unreal_loss_to_adj_equity`; robustness = `htm_loss_to_equity`. CAR column = `car_0_2`.
- ~~Change needed in `code/02_build_bank_measures.py`: currently divides by plain `total_equity`.~~ Done 11/7: the code now uses (total equity + AFS loss).

## Data source

- **Decided (Nov 9): stock returns now come from CRSP via WRDS for all 12 banks and SPY, replacing yfinance.** Reasons: consistency (one source for every bank) and to include delisted banks (SIVB, CMA), which Yahoo does not have.
- SPY stays the market benchmark, now also pulled from CRSP (PERMNO 84398).
- Banks are matched by **PERMNO via the PERMCO** in the NY Fed CRSP-FRB link file, never by ticker (delisted tickers can be reused).
- CRSP delisting returns are included where they apply. SIVB's delisting record (Mar 10, 2023) has no delisting return, so none is added.
- **Decided (Nov 9): days with no trade (CRSP price < 0, a bid/ask quote) are dropped.** This removes SIVB's quote-based Mar 10 return (−62.9%), so SIVB's CAR covers day 0 only.
- Rebuilding the returns needs a WRDS login (`code/03_download_crsp.py`). Raw CRSP files are git-ignored (license); only derived results go in `outputs/`.
- The old yfinance script is kept in `dev/` for reference only.

## Dashboard

- **Decided: Streamlit** (`app.py`), not an HTML page. Short Python is easier for every teammate to explain, which the course requires.
- Four tabs: Introduction, Methodology, Analysis (regression + scatter), Interactive fragility screen.
- Decided: skip the toy CSV. Mithran (A) takes care of all dashboard work through Saturday, Nov 14, on his own schedule. Risk: the app can't show data until the real merged file exists.

**Instruction for the coding agent (Claude Code):** the repo will be audited and every teammate must explain every step. Keep code short and plain Python, one clear purpose per section, a comment above each block saying what it does and why, no clever tricks or unused code. After each section, summarize in plain English what was built.

## Data work

- **Decided: Mithran builds the fundamentals data (link table, call reports, ratios) and the returns data (prices, event study) himself, with a coding agent.**
- Builds on the existing `code/02_build_bank_measures.py`.
- Teammates still need to be able to explain this code for the audit.

## Changes needed in repo (all done 11/7)

- README: rename `car_0_5` to `car_0_2`, update window definition, sample size for v0, loss-ratio denominator.
- `02_build_bank_measures.py`: adjust denominator; add holding-company aggregation; add HTM-only ratio.
- Add `DECISIONS.md` (this doc) and `CLAUDE.md` (agent instructions, "Mithran Moses, 11/7" at the top, tells the agent to read `DECISIONS.md` first) to the repo root. Add required files the course lists: `run_all.py` (or README run steps), `specs_tried.md`, `STATUS.md`, `audits/01_self_audit.md`.

## For the report / self-audit

- Convenience sample chosen knowing the outcome; v1 uses all listed banks.
- Survivorship: SIVB, SBNY, FRC, PACW failed or merged.
- SIVB stopped trading after Mar 9 (halted Mar 10, then seized), so its CAR covers only day 0. CRSP's Mar 10 return is a quote with no trade and is dropped (see "Data source").
- Uninsured deposits only reported by banks with at least $1B in assets.
- Window choice justified against news timeline; Credit Suisse on Mar 15.
- Loss-ratio choice and double-counting adjustment.
- Holding company vs. subsidiary aggregation method.
