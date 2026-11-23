# As-filed uninsured deposits from the 2022 10-Ks (instructor audit B3)

`uninsured_10k_2022q4.csv`: estimated uninsured deposits at 12/31/2022, as each holding company reported them in its 10-K for 2022. Every 10-K was filed between Feb 14 and Feb 28, 2023, **before** the event (Mar 9, 2023), so these are numbers investors could see. The call-report values we use are the current versions, which 9 of our 12 holding companies resubmitted after the event (`audits/amendments_check.md`).

**How collected (by hand, 2026-11-23, Lucas Koranda with Claude Code):**
1. The filing list came from SEC EDGAR's submissions API (`https://data.sec.gov/submissions/CIK##########.json`): the form 10-K with report date 2022-12-31.
2. Each document in `document_url` was opened and searched for "uninsured", "insurance limit" and "$250,000". For U.S. Bancorp and Wells Fargo, the MD&A is in the annual-report exhibit, so the URL points there.
3. `wording` holds the sentence fragment the number comes from.

**`comparable_to_call_report`** is True when the 10-K figure uses the same scope as the call-report item (RCON5597, U.S. offices, bank level). That means one of:
- it says it uses the regulatory or call-report method;
- it covers U.S. or domestic offices only;
- it uses the call report's definition.

It is False when the figure is firmwide or consolidated, or includes non-U.S. deposits (JPM, BAC, USB, WFC). Those differ from the call report for definitional reasons, so they cannot show what a resubmission changed.

- **Check that held:** for CMA and SIVB, which never resubmitted, the comparable 10-K figure matches the call report to within $0.1bn.
- **Check that failed, as expected:** for WFC, which also never resubmitted but uses consolidated scope, it is 29% lower.
