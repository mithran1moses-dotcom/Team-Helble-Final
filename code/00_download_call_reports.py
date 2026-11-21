"""
00_download_call_reports.py

Downloads one quarter of FFIEC call reports (bulk, all schedules, tab-delimited)
and unzips it into inputs/call_reports/<folder>/. Replaces the manual web-form
steps in inputs/call_reports/README.md (instructor audit A4).

Usage:
    python code/00_download_call_reports.py 2022Q4 12/31/2022    # event quarter
    python code/00_download_call_reports.py 2026Q3 09/30/2026    # latest quarter ("today" screen)

Source: https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx (public, no login)
Output: inputs/call_reports/<folder>/*.txt   (git-ignored; large)
        inputs/call_reports/<folder>/download.provenance.txt

How the site works: it is an ASP.NET web form. Each choice posts the whole form
back to the server with its hidden state fields (__VIEWSTATE etc.), so we:
  1. load the page,
  2. pick the product "Call Reports -- Single Period" (this fills the date list),
  3. pick the date and "Tab Delimited", and press Download.
"""

import io
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
URL = "https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx"
FORM = "ctl00$MainContentHolder$"  # prefix of every field name on the page
PRODUCT = "ReportingSeriesSinglePeriod"  # "Call Reports -- Single Period"

# Read the two arguments: output folder name and report date as the site writes it.
folder, report_date = sys.argv[1], sys.argv[2]
assert re.fullmatch(r"\d{2}/\d{2}/\d{4}", report_date), "date must look like 12/31/2022"
out_dir = ROOT / "inputs" / "call_reports" / folder


def hidden_fields(html):
    """Return the page's hidden ASP.NET state fields (they must be posted back)."""
    return dict(re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', html))


def date_options(html):
    """Return the date drop-down as {"12/31/2022": "<site's internal id>", ...}.
    The site shows the date as the option text and posts back a numeric id."""
    block = re.search(r'name="' + re.escape(FORM) + r'DatesDropDownList".*?</select>', html, re.S)
    options = re.findall(r'<option[^>]*value="([^"]+)"[^>]*>\s*([^<]+?)\s*<', block.group(0)) if block else []
    return {text: value for value, text in options}


# A session keeps the site's cookies between the three requests. Generic
# browser-like User-Agent, as in 01a (the site may reject requests without one).
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0"

# Step 1: load the empty form.
page = session.get(URL, timeout=60)
page.raise_for_status()

# Step 2: choose the product. This post-back makes the server fill the date list.
form = hidden_fields(page.text)
form.update({"__EVENTTARGET": FORM + "ListBox1", "__EVENTARGUMENT": "",
             FORM + "ListBox1": PRODUCT, FORM + "FormatType": "TSVRadioButton"})
page = session.post(URL, data=form, timeout=60)
page.raise_for_status()
dates = date_options(page.text)
assert dates, "the site returned no report dates; the form may have changed"
assert report_date in dates, f"{report_date} not offered; newest dates are {list(dates)[:4]}"

# Step 3: choose the date and tab-delimited format, and press Download.
# The reply should be a zip file (zip files start with the bytes "PK").
form = hidden_fields(page.text)
form.update({"__EVENTTARGET": "", "__EVENTARGUMENT": "",
             FORM + "ListBox1": PRODUCT, FORM + "DatesDropDownList": dates[report_date],
             FORM + "FormatType": "TSVRadioButton",
             FORM + "TabStrip1$Download_0": "Download"})
reply = session.post(URL, data=form, timeout=600)
reply.raise_for_status()
assert reply.content[:2] == b"PK", "the reply is not a zip file; the form may have changed"

# Unzip into the quarter's folder.
out_dir.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(io.BytesIO(reply.content)) as archive:
    names = archive.namelist()
    archive.extractall(out_dir)

# Check that the schedules code/02 reads are there (RC, RC-B parts, RC-O parts, POR).
stamp = report_date.replace("/", "")  # 12/31/2022 -> 12312022, as in the file names
for needed in ["Schedule RC ", "Schedule RCB ", "Schedule RCO ", "Bulk POR "]:
    assert any(needed in n and stamp in n for n in names), f"missing {needed.strip()} file"

# Write a provenance note next to the files. Also add a row to the pull log in
# inputs/call_reports/README.md by hand, with the "CDR data as of" date.
note = out_dir / "download.provenance.txt"
note.write_text(f"Source: {URL}\nProduct: Call Reports -- Single Period, Tab Delimited\n"
                f"Report date: {report_date}\nDownloaded: {date.today()} "
                f"by code/00_download_call_reports.py\nFiles: {len(names)}\n"
                f"Zip size (bytes): {len(reply.content)}\n")

print(f"Wrote {len(names)} files to {out_dir.relative_to(ROOT)}/ and {note.name}")
