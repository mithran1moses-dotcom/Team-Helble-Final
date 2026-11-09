"""
01a_download_nyfed_link.py

Downloads the New York Fed CRSP-FRB link file, which maps each listed bank
holding company's CRSP company ID (PERMCO) to its Federal Reserve ID (RSSD),
with the dates each link is valid.

Source page: https://www.newyorkfed.org/research/banking_research/crsp-frb
Output     : inputs/links/raw/crsp_20240930v2.csv  (git-ignored; re-run to rebuild)
"""

from datetime import date
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = ("https://www.newyorkfed.org/medialibrary/media/research/"
       "banking_research/data/crsp_20240930v2.csv")
OUT = ROOT / "inputs" / "links" / "raw" / "crsp_20240930v2.csv"

# Download the file. The NY Fed site rejects requests without a browser-like
# User-Agent, so we send a generic one.
OUT.parent.mkdir(parents=True, exist_ok=True)
request = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(request) as response:
    OUT.write_bytes(response.read())

# Check it is the file we expect: these columns, and more than a few rows.
header = OUT.read_text().splitlines()[0]
assert header == "name,inst_type,entity,permco,dt_start,dt_end", header
n_rows = len(OUT.read_text().splitlines()) - 1
assert n_rows > 1000, n_rows

# Write a provenance note next to the raw file.
note = OUT.with_suffix(".provenance.txt")
note.write_text(f"Source: {URL}\nDownloaded: {date.today()}\nRows: {n_rows}\n")

print(f"Wrote {OUT.relative_to(ROOT)} ({n_rows} rows) and {note.name}")
