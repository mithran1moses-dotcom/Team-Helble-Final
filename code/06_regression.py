"""
06_regression.py

Main regression (stub for v0) and the headline scatter.

    car_0_2 = a + b1*uninsured_dep_share + b2*unreal_loss_to_adj_equity + b3*log_total_assets + e
    with HC3 heteroskedasticity-robust standard errors and t-based p-values.

Main sample: banks that did NOT fail inside the event window (failed_in_window
is False). SIVB's collapse is the shock itself and its CAR covers day 0 only, so
it is left out (instructor audit A1). The with-SIVB version is the robustness
run in code/06c_robustness_with_failed.py.

Why HC3 with t p-values (instructor audit A2): with ~8 residual degrees of
freedom, HC1 with normal (z) p-values overstates significance; HC3 is the
better small-sample choice, and use_t=True reports t-statistics.

Input : outputs/analysis_sample.csv  (code/05_build_analysis_sample.py)
Output: outputs/regression_main.csv              coefficients, robust SEs, t p-values, N
        outputs/regression_main.txt              full statsmodels summary
        outputs/figures/scatter_loss_vs_car.png  unreal_loss_to_adj_equity vs car_0_2

v0 caveat: with 11 banks and 4 coefficients, this is a pipeline check, not evidence.
Every spec run must be logged in specs_tried.md.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw to a file, no window
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
sample = pd.read_csv(OUT / "analysis_sample.csv")

# 1. Main sample: drop banks that failed inside the event window (SIVB in v0),
#    then keep banks with every variable. All 11 remaining banks must be used:
#    stop if any bank drops out for a missing value.
formula = "car_0_2 ~ uninsured_dep_share + unreal_loss_to_adj_equity + log_total_assets"
failed = sample[sample["failed_in_window"]]
assert failed["ticker"].tolist() == ["SIVB"], failed["ticker"].tolist()
used = sample[~sample["failed_in_window"]].dropna(
    subset=["car_0_2", "uninsured_dep_share", "unreal_loss_to_adj_equity", "log_total_assets"])
assert len(sample) == 12 and len(used) == 11, f"only {len(used)} of 11 non-failed banks usable"

# 2. OLS with HC3 robust errors; use_t=True gives t-statistics and t p-values.
fit = smf.ols(formula, data=used).fit(cov_type="HC3", use_t=True)
assert int(fit.nobs) == 11

# 3. Save a tidy coefficient table and the full summary (both feed the dashboard and report).
table = pd.DataFrame({"term": fit.params.index, "coef": fit.params.values,
                      "robust_se": fit.bse.values, "t_stat": fit.tvalues.values,
                      "p_value": fit.pvalues.values})
table["cov_type"] = "HC3, t p-values"
table["n_obs"] = int(fit.nobs)
table["r_squared"] = fit.rsquared
table["banks_used"] = ", ".join(used["ticker"])
table.to_csv(OUT / "regression_main.csv", index=False)
(OUT / "regression_main.txt").write_text(str(fit.summary()))

# 4. Scatter: x = main loss ratio, y = CAR. Dot area grows with the uninsured
#    deposit share; each dot is labeled with its ticker. The banks in the main
#    regression are solid blue; failed banks (SIVB) are hollow gray, shown for
#    context but not in the regression.
BLUE, INK, MUTED, SURFACE = "#2a78d6", "#0b0b0b", "#52514e", "#fcfcfb"
fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
ax.scatter(used["unreal_loss_to_adj_equity"], used["car_0_2"],
           s=used["uninsured_dep_share"] * 300, color=BLUE, alpha=0.85,
           edgecolor=SURFACE, linewidth=2, zorder=3)
ax.scatter(failed["unreal_loss_to_adj_equity"], failed["car_0_2"],
           s=failed["uninsured_dep_share"] * 300, facecolor="none",
           edgecolor=MUTED, linewidth=1.5, zorder=3)
for row in used.itertuples():
    ax.annotate(row.ticker, (row.unreal_loss_to_adj_equity, row.car_0_2),
                xytext=(7, 4), textcoords="offset points", fontsize=9, color=INK)
for row in failed.itertuples():
    ax.annotate(f"{row.ticker} (failed, not in regression)", (row.unreal_loss_to_adj_equity, row.car_0_2),
                xytext=(-10, 8), textcoords="offset points", fontsize=9, color=MUTED, ha="right")

# Recessive axes and grid, plus a zero line for "no abnormal return".
ax.axhline(0, color=MUTED, linewidth=0.8, zorder=1)
ax.grid(color="#e4e3df", linewidth=0.6, zorder=0)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
for side in ["left", "bottom"]:
    ax.spines[side].set_color(MUTED)
ax.tick_params(colors=MUTED, labelsize=9)
ax.set_xlabel("Unrealized securities losses / adjusted equity (12/31/2022)", color=INK, fontsize=10)
ax.set_ylabel("CAR, Mar 9–13, 2023 (days 0 to +2)", color=INK, fontsize=10)

ax.set_title(f"Securities losses vs. stock reaction to SVB's failure ({len(used)} banks + SIVB)",
             color=INK, fontsize=11, loc="left")
fig.text(0.01, 0.01, "Dot size = uninsured deposit share. Hollow = failed in the window, not in the regression;\n"
         "SIVB's CAR covers day 0 only (stopped trading after Mar 9). "
         "Returns: CRSP via WRDS. Source: outputs/analysis_sample.csv", color=MUTED, fontsize=8)
fig.tight_layout(rect=(0, 0.07, 1, 1))
# Make the figures folder if it is missing (e.g. a rebuild from an empty outputs/).
(OUT / "figures").mkdir(parents=True, exist_ok=True)
fig.savefig(OUT / "figures" / "scatter_loss_vs_car.png", dpi=200)

print(f"Regression on {int(fit.nobs)} banks, failed banks excluded (HC3 robust SEs, t p-values):")
print(table[["term", "coef", "robust_se", "t_stat", "p_value"]].round(4).to_string(index=False))
print(f"R-squared: {fit.rsquared:.3f}")
print("Wrote outputs/regression_main.csv, regression_main.txt, figures/scatter_loss_vs_car.png")
