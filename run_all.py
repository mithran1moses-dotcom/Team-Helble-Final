"""
run_all.py: rebuild every file in outputs/ from the raw inputs, in order.

    python run_all.py              rebuild outputs from the inputs already on disk
    python run_all.py --download   first re-download the inputs that a script can fetch
                                   (NY Fed link file, CRSP returns from WRDS) and rebuild the link table.
                                   The CRSP step asks for your WRDS username and password.

Inputs that must be downloaded by hand first (see each folder's README):
    inputs/call_reports/2022Q4/    FFIEC call reports, 12/31/2022
    inputs/links/raw/nic/          FFIEC NIC relationships and attributes
    inputs/prices/crsp/            CRSP daily returns for all 12 banks and SPY: run
                                   code/03_download_crsp.py once (needs a WRDS login);
                                   the files are git-ignored (WRDS license)

Why --download is off by default: the CRSP pull needs a WRDS login, and the link
table carries hand-check marks that 01b refuses to overwrite.
"""

import subprocess
import sys

# Each step is one script plus its arguments, in the order the pipeline needs.
DOWNLOAD_STEPS = [
    ["code/01a_download_nyfed_link.py"],
    ["code/01b_build_link_table.py"],
    ["code/03_download_crsp.py"],
]
TEST_STEPS = [
    # Check the measure code on fake data with hand-computed answers before using real data.
    ["dev/make_fake_call_reports.py"],
    ["code/02_build_bank_measures.py", "FAKE", "12312022"],
    ["dev/check_fake_bhc_measures.py"],
]
BUILD_STEPS = [
    ["code/02_build_bank_measures.py", "2022Q4", "12312022"],  # call reports -> bank and BHC measures
    ["code/04_event_study.py"],                                # CRSP returns -> car_0_2
    ["code/05_build_analysis_sample.py"],                      # merge -> analysis_sample.csv (12 rows)
    ["code/06_regression.py"],                                 # regression table and scatter
]

steps = (DOWNLOAD_STEPS if "--download" in sys.argv else []) + TEST_STEPS + BUILD_STEPS

# Run each step with the same Python as this script. check=True stops at the
# first failure, so a broken step never feeds stale files to the next one.
for step in steps:
    print(f"\n=== {' '.join(step)} ===", flush=True)
    subprocess.run([sys.executable, *step], check=True)

print("\nAll steps finished. Outputs are in outputs/.")
