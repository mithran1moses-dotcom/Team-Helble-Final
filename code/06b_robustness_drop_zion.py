"""
06b_robustness_drop_zion.py

Robustness check for the AFS-to-HTM transfer limitation: rerun the main
regression (same formula and HC1 errors as code/06_regression.py) without Zions.

Why: Zions moved securities from AFS to HTM. The loss locked in at the transfer
sits in equity (AOCI), not in HTM cost minus fair value, so its HTM loss comes
out negative and its loss ratio is understated. Decided 11/14 (DECISIONS.md):
keep this as a stated limitation, and check that the main result does not hinge on ZION.

Input : outputs/analysis_sample.csv  (code/05_build_analysis_sample.py)
Output: outputs/regression_drop_zion.csv   coefficients, robust SEs, p-values, N
        outputs/regression_drop_zion.txt   full statsmodels summary
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
sample = pd.read_csv(OUT / "analysis_sample.csv")

# 1. Drop Zions and keep banks with every variable. ZION must be in the sample
#    to begin with, and the other 11 banks must all be usable.
formula = "car_0_2 ~ uninsured_dep_share + unreal_loss_to_adj_equity + log_total_assets"
assert (sample["ticker"] == "ZION").sum() == 1, "ZION not found exactly once"
used = sample[sample["ticker"] != "ZION"].dropna(
    subset=["car_0_2", "uninsured_dep_share", "unreal_loss_to_adj_equity", "log_total_assets"])
assert len(used) == 11, f"expected 11 banks without ZION, got {len(used)}"
fit = smf.ols(formula, data=used).fit(cov_type="HC1")

# 2. Save the same tidy table and full summary as the main regression.
table = pd.DataFrame({"term": fit.params.index, "coef": fit.params.values,
                      "robust_se": fit.bse.values, "p_value": fit.pvalues.values})
table["n_obs"] = int(fit.nobs)
table["r_squared"] = fit.rsquared
table["banks_used"] = ", ".join(used["ticker"])
table.to_csv(OUT / "regression_drop_zion.csv", index=False)
(OUT / "regression_drop_zion.txt").write_text(str(fit.summary()))

print(f"Robustness, without ZION: {int(fit.nobs)} banks (HC1 robust SEs):")
print(table[["term", "coef", "robust_se", "p_value"]].round(4).to_string(index=False))
print(f"R-squared: {fit.rsquared:.3f}")
print("Wrote outputs/regression_drop_zion.csv, regression_drop_zion.txt")
