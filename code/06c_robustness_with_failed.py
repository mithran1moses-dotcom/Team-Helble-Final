"""
06c_robustness_with_failed.py

Robustness check for the failed-bank rule (instructor audit A1): rerun the main
regression (same formula and HC3 errors as code/06_regression.py) with the
banks that failed inside the event window put back in. In v0 that is SIVB only.

Why: the main spec leaves SIVB out because its collapse is the shock itself and
its CAR covers day 0 only. This run shows how much the slopes depend on it.
It is the v0 main spec (specs_tried.md #3) with HC3 errors and t p-values.

Input : outputs/analysis_sample.csv  (code/05_build_analysis_sample.py)
Output: outputs/regression_with_failed.csv   coefficients, robust SEs, t p-values, N
        outputs/regression_with_failed.txt   full statsmodels summary
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
sample = pd.read_csv(OUT / "analysis_sample.csv")

# 1. Every bank, failed or not, with every variable. SIVB must be in the
#    sample and flagged as failed, and all 12 banks must be usable.
formula = "car_0_2 ~ uninsured_dep_share + unreal_loss_to_adj_equity + log_total_assets"
assert sample.loc[sample["failed_in_window"], "ticker"].tolist() == ["SIVB"]
used = sample.dropna(
    subset=["car_0_2", "uninsured_dep_share", "unreal_loss_to_adj_equity", "log_total_assets"])
assert len(used) == 12, f"expected 12 banks with SIVB, got {len(used)}"
fit = smf.ols(formula, data=used).fit(cov_type="HC3", use_t=True)

# 2. Save the same tidy table and full summary as the main regression.
table = pd.DataFrame({"term": fit.params.index, "coef": fit.params.values,
                      "robust_se": fit.bse.values, "t_stat": fit.tvalues.values,
                      "p_value": fit.pvalues.values})
table["cov_type"] = "HC3, t p-values"
table["n_obs"] = int(fit.nobs)
table["r_squared"] = fit.rsquared
table["banks_used"] = ", ".join(used["ticker"])
table.to_csv(OUT / "regression_with_failed.csv", index=False)
(OUT / "regression_with_failed.txt").write_text(str(fit.summary()))

print(f"Robustness, failed banks put back in: {int(fit.nobs)} banks (HC3 robust SEs, t p-values):")
print(table[["term", "coef", "robust_se", "t_stat", "p_value"]].round(4).to_string(index=False))
print(f"R-squared: {fit.rsquared:.3f}")
print("Wrote outputs/regression_with_failed.csv, regression_with_failed.txt")
