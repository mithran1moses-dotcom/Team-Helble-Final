# FFIEC Call Reports: provenance

**Source:** FFIEC Central Data Repository (CDR), Public Data Distribution
<https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx>

**How to re-download (scripted, added 11/21 for instructor audit A4):**

```bash
python code/00_download_call_reports.py 2022Q4 12/31/2022
```

The script fills in the same web form (product, date, tab-delimited) and unzips into
`inputs/call_reports/2022Q4/`. Use another folder and date for the latest quarter, e.g.
`python code/00_download_call_reports.py 2026Q3 09/30/2026`. Then add a row to the pull log below.

**By hand, if the script breaks (the site is a web form):**
1. Available Products → **Call Reports -- Single Period**
2. Reporting Period → **12/31/2022** (the last quarter-end *before* SVB failed on 3/10/2023)
3. Format → **Tab Delimited** → Download
4. Unzip into `inputs/call_reports/2022Q4/` so that files look like
   `inputs/call_reports/2022Q4/FFIEC CDR Call Schedule RCB 12312022(1 of 2).txt`

For the "today" fragility screen, repeat with the latest available quarter into its own folder
(e.g. `inputs/call_reports/2026Q2/`).

**Pull log** (fill in every time someone downloads):

| Period | Downloaded on | By | Notes |
|---|---|---|---|
| 12/31/2022 | 2026-11-07 | Mithran (via Claude in Chrome) | `FFIEC CDR Call Bulk All Schedules 12312022.zip`, 51 files, CDR data as of 2026-09-15. RC-O now comes in 2 parts. |
| 12/31/2022 | 2026-11-21 | Lucas (`code/00_download_call_reports.py`, with Claude Code) | Same 51 files, 6.9 MB zip, CDR data as of 2026-09-15 (same vintage as above). Rebuilding `02`–`06` from it reproduced every committed output (only the clock time in `regression_main.txt` differs). |

**Format notes:**
- One file per schedule; big schedules are split into parts, e.g. `(1 of 2)`, `(2 of 2)`.
- Row 1 holds MDRM codes (e.g. `RCFD1754`). **Row 2 holds text descriptions, not data.**
- `IDRSSD` is the bank's Federal Reserve ID; it's the merge key across schedules.
- `RCFD` fields = consolidated incl. foreign offices (FFIEC 031 filers only).
  `RCON` fields = domestic offices (everyone). The parser takes RCFD when present, else RCON.
- The raw `.txt`/`.zip` files are git-ignored (they're large).
