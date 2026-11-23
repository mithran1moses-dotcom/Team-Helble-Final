"""
06d_robustness_not_resubmitted.py

Robustness check for look-ahead through resubmitted call reports (instructor
audit B3): rerun the main regression (same formula, sample and HC3 errors as
code/06_regression.py, so failed banks are already out) on only the holding
companies whose 12/31/2022 call reports were NOT resubmitted after Mar 9, 2023
(resubmitted_after_event is False). Their numbers are what the market saw.

At v0 only 2 banks are left (CMA, WFC), fewer than the 4 coefficients, so the
regression cannot be estimated. The script then writes a one-row file saying so,
instead of stopping the pipeline. In v1 (about 100 banks, ~59% not resubmitted)
it runs the regression.

Input : outputs/analysis_sample.csv  (code/05_build_analysis_sample.py)
Output: outputs/regression_not_resubmitted.csv   coefficients, robust SEs, t p-values, N
        outputs/regression_not_resubmitted.txt   full statsmodels summary, or why not estimated
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
sample = pd.read_csv(OUT / "analysis_sample.csv")

# 1. Main sample (failed banks out), then keep only holding companies whose
#    reports were not resubmitted after day 0, with every variable.
formula = "car_0_2 ~ uninsured_dep_share + unreal_loss_to_adj_equity + log_total_assets"
used = sample[~sample["failed_in_window"] & ~sample["resubmitted_after_event"]].dropna(
    subset=["car_0_2", "uninsured_dep_share", "unreal_loss_to_adj_equity", "log_total_assets"])

# 2. Fewer than 10 banks for 4 coefficients is not a regression worth reporting
#    (at 2 banks it cannot be computed at all). Record that and stop here.
MIN_BANKS = 10
if len(used) < MIN_BANKS:
    note = (f"Not estimated: only {len(used)} non-failed banks have call reports not "
            f"resubmitted after Mar 9, 2023 ({', '.join(used['ticker'])}); need at least {MIN_BANKS}.")
    pd.DataFrame({"term": ["not estimated"], "n_obs": [len(used)],
                  "banks_used": [", ".join(used["ticker"])], "note": [note]}
                 ).to_csv(OUT / "regression_not_resubmitted.csv", index=False)
    (OUT / "regression_not_resubmitted.txt").write_text(note + "\n")
    print(note)
    print("Wrote outputs/regression_not_resubmitted.csv, regression_not_resubmitted.txt")
    raise SystemExit(0)

# 3. Otherwise, the same regression and the same tidy table as the main spec.
fit = smf.ols(formula, data=used).fit(cov_type="HC3", use_t=True)
table = pd.DataFrame({"term": fit.params.index, "coef": fit.params.values,
                      "robust_se": fit.bse.values, "t_stat": fit.tvalues.values,
                      "p_value": fit.pvalues.values})
table["cov_type"] = "HC3, t p-values"
table["n_obs"] = int(fit.nobs)
table["r_squared"] = fit.rsquared
table["banks_used"] = ", ".join(used["ticker"])
table.to_csv(OUT / "regression_not_resubmitted.csv", index=False)
(OUT / "regression_not_resubmitted.txt").write_text(str(fit.summary()))

print(f"Robustness, reports not resubmitted after the event: {int(fit.nobs)} banks (HC3, t p-values):")
print(table[["term", "coef", "robust_se", "t_stat", "p_value"]].round(4).to_string(index=False))
print("Wrote outputs/regression_not_resubmitted.csv, regression_not_resubmitted.txt")
