# FFIEC Call Reports: provenance

**Source:** FFIEC Central Data Repository (CDR), Public Data Distribution
<https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx>

**How to re-download (manual; the site is a web form):**
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
| 12/31/2022 | YYYY-MM-DD | name | |

**Format notes:**
- One file per schedule; big schedules are split into parts, e.g. `(1 of 2)`, `(2 of 2)`.
- Row 1 holds MDRM codes (e.g. `RCFD1754`). **Row 2 holds text descriptions, not data.**
- `IDRSSD` is the bank's Federal Reserve ID; it's the merge key across schedules.
- `RCFD` fields = consolidated incl. foreign offices (FFIEC 031 filers only).
  `RCON` fields = domestic offices (everyone). The parser takes RCFD when present, else RCON.
- The raw `.txt`/`.zip` files are git-ignored (they're large).
