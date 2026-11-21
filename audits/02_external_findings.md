# External findings, 2026-11-16

Evidence from outside the repo that bears on findings 10 and 17 in `audits/01_self_audit.md`.

**Prepared:** 2026-11-16, by Mithran Moses with Claude.
**Reviewed by a person:** _name, date_ (read this file, open the sources, and confirm the two claims below).

No code, inputs or outputs changed. Every figure here comes from a public source outside the project and is cited at the bottom; nothing in this file traces to `outputs/`, which is why it lives in `audits/` and not in the README.

## 1. Finding 10 (call report amendments) is confirmed at the industry level

Finding 10 says: the FFIEC bulk files downloaded in Nov 2026 show the latest amended values, so if a bank amended its 12/31/2022 report after Mar 9, 2023 we use numbers the market did not have. It is marked "Plausible, not checked."

It is no longer only plausible. The restatement wave is documented, dated, and large:

- On **July 24, 2023** the FDIC issued a Financial Institution Letter telling banks that estimated uninsured deposits must include **intercompany deposits from subsidiaries** and **deposits collateralized by pledged assets**, and asking institutions that had incorrectly reduced their figures to amend their call reports.
- By August 2023, **117 companies had restated their Q4 2022 uninsured deposit data**, a net decline of **$281.39 billion** from the originally filed values.
- The largest single downward adjustment by dollar amount was **Bank of America, $125.34 billion**.

Q4 2022 is this project's measurement quarter and Bank of America is one of the 12 holding companies, so the exposure is direct rather than theoretical.

Two consequences:

**The variable is vintage-dependent.** `uninsured_dep_share` is built from whatever vintage the extract carries. If it carries amended values, the numerator partly reflects a definition clarified in July 2023 and applied retroactively — information no investor had on March 9, 2023. This is a look-ahead channel that enters through the source's revision history, not through the code, which is why the merge and leakage checks (findings 17–19) all pass while this one stays open.

**The intercompany rule interacts with the aggregation step.** `code/02` sums dollars across subsidiaries before taking the ratio. If a subsidiary's deposits held at a sibling bank are counted as uninsured at the holding end, summing across subsidiaries of one parent can count the same balances twice. The parents at risk are the multi-subsidiary ones in `inputs/links/bank_link_v0.csv`: WFC (4 bank subsidiaries), JPM (3), and BAC, CMA, TFC and USB (2 each). This sharpens finding 21, which already notes the numerator and denominator are built from different subsidiary sets.

### Suggested extension to the v1 plan

The B2 plan for finding 10 is to check the POR file's "last updated" date for the 19 filing banks and, for any updated after Mar 9, 2023, find the originally filed values or flag the bank. That still holds. Two additions now that the cause is known:

1. Treat **July 24, 2023** as the date of interest alongside Mar 9, 2023. Amendments cluster after the FDIC letter, and an amendment that post-dates the letter is almost certainly a definitional restatement rather than a correction of a typo.
2. For the six multi-subsidiary parents, check whether intercompany balances are now included on both sides of the sum. If they are, the v1 robustness check for finding 21 should also report a version that nets them out.

**Status after this file:** finding 10 goes from "Plausible, not checked" to "Real at the industry level; not yet checked bank-by-bank for our 12." The bank-level check is still open and still due in v1.

## 2. Why CMA is delisted (finding 17, and the PR #2 text)

Finding 17 and the Checkpoint 1 PR description both describe SIVB and CMA as delisted. For SIVB the reason is obvious. For Comerica it reads as an error, because Comerica traded on the NYSE throughout 2023 and was never seized.

It is not an error. **Comerica's merger into Fifth Third Bancorp closed on February 1, 2026**, ending Comerica's existence as an independent public company. Shareholders received 1.8663 Fifth Third shares per Comerica share, and Comerica common and Series B preferred stock were delisted from the NYSE. The all-stock deal was announced in October 2025 and created the ninth-largest U.S. bank, at roughly $294 billion in assets.

So the November 2026 failure to pull CMA from Yahoo and Nasdaq was caused by a 2026 corporate action, not by anything in March 2023. CRSP retains delisted securities permanently, which is why it was the correct source for both banks even though they left the tape for completely different reasons — and why the PERMNO-through-PERMCO match described in finding 17 is the right matching strategy.

**No effect on the event study.** Comerica and Fifth Third were independent companies in March 2023, every measure is taken at 12/31/2022, and the returns used are the ones those two separate securities actually produced. Nothing in `code/03`–`code/06` needs to change.

Worth stating in the write-up anyway: "delisted" sitting next to SIVB invites a reader to assume Comerica failed too.

## 3. Consequence for the "fragile today" question

FITB and CMA are both in the 12-bank sample, and since February 2026 they are one company.

The README's second question — using the same measures, which listed banks look most fragile **today** — and the dashboard's Interactive fragility screen both present the 12-bank roster as a current view. Two of those rows are now the same institution, and one of them no longer trades.

Options, in increasing order of effort:

1. Label the screen and the README question explicitly as a March 2023 snapshot rather than a current view. One sentence, no code.
2. Add a note on the CMA row recording the February 2026 merger into Fifth Third.
3. Treat "fragile today" as a v1 question needing a current call-report pull and a current roster. This is the honest version and is well beyond v0 scope.

Option 1 is the minimum before anyone demonstrates that tab.

## Sources

| Claim | Source |
|---|---|
| FDIC July 24, 2023 guidance: intercompany and collateralized deposits must be included | [S&P Global Market Intelligence, 2023-07-24](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2023/7/fdic-banks-must-include-intercompany-deposits-in-uninsured-deposit-total-76665714) |
| 117 companies restated Q4 2022 uninsured deposits, net −$281.39bn | [S&P Global Market Intelligence, 2023-08](https://www.spglobal.com/market-intelligence/en/news-insights/articles/2023/8/banks-race-to-restate-uninsured-deposit-totals-after-fdic-guidance-76988676) |
| Bank of America's $125.34bn downward adjustment | [Weiss Ratings](https://weissratings.com/en/weiss-ratings-daily/weiss-bank-ratings-filter-the-fluff) |
| FDIC warned banks over uninsured deposit reporting errors | [Bloomberg Law, 2023-07-25](https://news.bloomberglaw.com/banking-law/fdic-warns-banks-after-errors-in-reporting-uninsured-deposits) |
| Comerica merger closed Feb 1 2026, 1.8663 exchange ratio, NYSE delisting | [Comerica 8-K via Stock Titan](https://www.stocktitan.net/sec-filings/CMA/8-k-comerica-inc-reports-material-event-e5723bba6ec3.html) |
| Deal announced Oct 2025, ninth-largest U.S. bank, ~$294bn assets | [Fifth Third closing announcement via Nasdaq, 2026-02-02](https://www.nasdaq.com/press-release/fifth-third-completes-merger-comerica-become-9th-largest-us-bank-2026-02-02) |

Before this is cited in a graded write-up, replace the trade coverage with the primary documents: the FDIC's July 24, 2023 Financial Institution Letter on estimated uninsured deposits, and Comerica's own 8-K.
