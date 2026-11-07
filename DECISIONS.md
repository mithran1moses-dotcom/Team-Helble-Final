# DECISIONS.md — Team Helble

Running list of open decisions, settled decisions, and things the report or self-audit must mention.
Add the date and your name to every entry. Started 2026-11-07 by Mithran.

## Open — need a team decision

1. **Event window.** README says `car_0_5` (Mar 9–16). Plan doc says Mar 9–13. Mar 15 includes the Credit Suisse shock. Pick a main window and a robustness window.
2. **Day 0.** Mar 9 (first trading reaction) or Mar 10 (seizure)? README says show both.
3. **Estimation window.** README says it ends before 2023; plan doc says late Feb 2023.
4. **Loss ratio.** HTM + AFS losses (current code) or HTM only? Which equity denominator, given AFS losses are already in equity?
5. **v0 sample.** 12 banks (plan doc) or ~100 (README)? Is PACW in?
6. **Unit of observation.** Holding company (README) vs. bank subsidiary (what the code produces). How to aggregate.
7. **Column names.** Freeze the final schema; A owns it.

## Decided

- Balance-sheet data from the 12/31/2022 call report (no look-ahead).
- Market model vs. SPY.

## For the report / self-audit

- Convenience sample chosen knowing the outcome; v1 uses all listed banks.
- Survivorship: SIVB, SBNY, FRC, PACW failed or merged; yfinance may lack their data.
- SIVB stopped trading Mar 10, so its CAR covers only day 0.
- Uninsured deposits only reported by banks with assets of at least $1B.
- Illiquid small banks have noisy returns; size and liquidity filters are logged.
- Link quality: report the match rate and hand-checked sample.
