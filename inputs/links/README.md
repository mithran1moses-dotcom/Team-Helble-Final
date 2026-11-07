# Link files: provenance

These files connect each stock ticker to its bank holding company (BHC) and to the
bank subsidiaries that file call reports. Built by `code/01a_download_nyfed_link.py`
and `code/01b_build_link_table.py`.

## Committed files

- `v0_banks.csv`: hand-entered. The 12 v0 tickers and each holding company's name exactly as
  the NY Fed file spells it. The NY Fed file has no tickers, so this name is the match key.
- `bank_link_v0.csv`: built by `code/01b_build_link_table.py`. One row per bank subsidiary.
  **Every row must be hand-checked** (fill `checked_by` and `checked_on`). The script refuses
  to overwrite the file once any row is checked.
- `poc_banks_handmap_TEMPLATE.csv`: the original template (kept for reference).

## Raw files (git-ignored, in `raw/`)

**NY Fed CRSP-FRB link file**: downloaded by script.
Source: <https://www.newyorkfed.org/research/banking_research/crsp-frb>, file `crsp_20240930v2.csv`.
Run `python code/01a_download_nyfed_link.py`. A provenance note is written next to it.

**FFIEC NIC bulk data**: manual download (the site blocks scripts).
1. Go to <https://www.ffiec.gov/npw/FinancialReport/DataDownload>
2. Under **CSV Download**, click **Relationships**, **Attributes- Active**, and **Attributes- Closed**
   (Closed is needed: SVB and Comerica no longer exist).
3. Unzip all three into `inputs/links/raw/nic/`, keeping the file names
   (`CSV_RELATIONSHIPS.CSV`, `CSV_ATTRIBUTES_ACTIVE.CSV`, `CSV_ATTRIBUTES_CLOSED.CSV`).

Note: the NIC attribute files hold only each institution's **latest** record, not its history.
The as-of-12/31/2022 date is applied to the relationships file only.

**Pull log** (fill in every time someone downloads):

| File | Downloaded on | By | Notes |
|---|---|---|---|
| NY Fed crsp_20240930v2.csv | 2026-11-07 | Mithran (script) | 1,495 rows |
| NIC Relationships, Attributes Active, Attributes Closed (CSV) | 2026-11-07 | Mithran | files dated 2026-11-06 |
