# Status

Update this whenever a pipeline step is finished or blocked. Add the date and your name.

## Deadlines (from DECISIONS.md)

- v0 checkpoint + proposal (HW8): Sat Nov 14
- v1 full-sample results: Sat Nov 21
- Working groups fix audit findings: Tue Nov 24
- Presentations: Dec 1 / Dec 3

## Pipeline steps

| Step | What | Status | Notes |
|---|---|---|---|
| 0 | Setup files (CLAUDE.md, README, logs) | Done 11/7 (Mithran, with Claude Code) | README matches DECISIONS.md |
| 1 | Link table (`inputs/links/bank_link_v0.csv`) | Built 11/7, awaiting hand-check | 21 bank subsidiaries for 12 BHCs; 2 rows have no NIC name (60143, 212465) |
| 2 | Call-report measures, holding-company level | | |
| 3 | Prices and event study (`car_0_2`) | | |
| 4 | Merge and regression | | |
| 5 | Streamlit dashboard (`app.py`) | | |
| 6 | `run_all.py` and self-audit | | |

## Blocked / waiting on

- Hand-check of all 21 rows in `inputs/links/bank_link_v0.csv` (fill `checked_by`, `checked_on`).

## Next up
