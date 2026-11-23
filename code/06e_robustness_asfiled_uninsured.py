"""
06e_robustness_asfiled_uninsured.py

Robustness check for look-ahead in the uninsured-deposit measure (instructor
audit B3): rerun the main regression (same formula, sample and HC3 errors as
code/06_regression.py, so failed banks are out) with the uninsured share the
market could have seen before the event, where we have it.

    uninsured share used = uninsured_dep_share_asfiled (code/05b) where available,
                           else the current call-report share (JPM, BAC, USB: their
                           10-K figures have a different scope, so no as-filed value)

The loss ratio and size are unchanged. Comparing this with the main spec shows
how much the resubmissions move the uninsured-share coefficient.

Inputs : outputs/analysis_sample.csv, outputs/asfiled_uninsured_comparison.csv
Output : outputs/regression_asfiled_uninsured.csv   coefficients, robust SEs, t p-values, N
         outputs/regression_asfiled_uninsured.txt   full statsmodels summary
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
sample = pd.read_csv(OUT / "analysis_sample.csv")
asfiled = pd.read_csv(OUT / "asfiled_uninsured_comparison.csv")

# 1. Main sample (failed banks out), with the as-filed share where we have it.
#    The as-filed column keeps the same name as in the main spec, so the formula
#    and the coefficient names stay the same.
used = sample[~sample["failed_in_window"]].merge(
    asfiled[["ticker", "uninsured_dep_share_asfiled"]], on="ticker", how="left", validate="1:1")
used["asfiled_available"] = used["uninsured_dep_share_asfiled"].notna()
used["uninsured_dep_share"] = used["uninsured_dep_share_asfiled"].fillna(used["uninsured_dep_share"])
used = used.dropna(subset=["car_0_2", "uninsured_dep_share", "unreal_loss_to_adj_equity", "log_total_assets"])
assert len(used) == 11, f"expected the 11 banks of the main spec, got {len(used)}"
assert sorted(used.loc[~used["asfiled_available"], "ticker"]) == ["BAC", "JPM", "USB"]

# 2. Same regression and the same tidy table as the main spec.
formula = "car_0_2 ~ uninsured_dep_share + unreal_loss_to_adj_equity + log_total_assets"
fit = smf.ols(formula, data=used).fit(cov_type="HC3", use_t=True)
table = pd.DataFrame({"term": fit.params.index, "coef": fit.params.values,
                      "robust_se": fit.bse.values, "t_stat": fit.tvalues.values,
                      "p_value": fit.pvalues.values})
table["cov_type"] = "HC3, t p-values"
table["n_obs"] = int(fit.nobs)
table["r_squared"] = fit.rsquared
table["banks_used"] = ", ".join(used["ticker"])
table["banks_current_share"] = ", ".join(used.loc[~used["asfiled_available"], "ticker"])
table.to_csv(OUT / "regression_asfiled_uninsured.csv", index=False)
(OUT / "regression_asfiled_uninsured.txt").write_text(str(fit.summary()))

print(f"Robustness, as-filed uninsured share: {int(fit.nobs)} banks (HC3, t p-values):")
print(table[["term", "coef", "robust_se", "t_stat", "p_value"]].round(4).to_string(index=False))
print("Wrote outputs/regression_asfiled_uninsured.csv, regression_asfiled_uninsured.txt")
