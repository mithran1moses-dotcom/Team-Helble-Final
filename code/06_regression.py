"""
06_regression.py

Main regression (stub for v0) and the headline scatter.

    car_0_2 = a + b1*uninsured_dep_share + b2*unreal_loss_to_adj_equity + b3*log_total_assets + e
    with heteroskedasticity-robust (HC1) standard errors.

Input : outputs/analysis_sample.csv  (code/05_build_analysis_sample.py)
Output: outputs/regression_main.csv              coefficients, robust SEs, p-values, N
        outputs/regression_main.txt              full statsmodels summary
        outputs/figures/scatter_loss_vs_car.png  unreal_loss_to_adj_equity vs car_0_2

v0 caveat: with 10-12 banks and 4 coefficients, this is a pipeline check, not evidence.
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

# 1. Regression on the banks that have every variable (rows missing car_0_2 drop out).
formula = "car_0_2 ~ uninsured_dep_share + unreal_loss_to_adj_equity + log_total_assets"
used = sample.dropna(subset=["car_0_2", "uninsured_dep_share", "unreal_loss_to_adj_equity", "log_total_assets"])
fit = smf.ols(formula, data=used).fit(cov_type="HC1")

# 2. Save a tidy coefficient table and the full summary (both feed the dashboard and report).
table = pd.DataFrame({"term": fit.params.index, "coef": fit.params.values,
                      "robust_se": fit.bse.values, "p_value": fit.pvalues.values})
table["n_obs"] = int(fit.nobs)
table["r_squared"] = fit.rsquared
table["banks_used"] = ", ".join(used["ticker"])
table.to_csv(OUT / "regression_main.csv", index=False)
(OUT / "regression_main.txt").write_text(str(fit.summary()))

# 3. Scatter: x = main loss ratio, y = CAR. Dot area grows with the uninsured
#    deposit share; each dot is labeled with its ticker. One series, so one color.
BLUE, INK, MUTED, SURFACE = "#2a78d6", "#0b0b0b", "#52514e", "#fcfcfb"
fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
ax.scatter(used["unreal_loss_to_adj_equity"], used["car_0_2"],
           s=used["uninsured_dep_share"] * 300, color=BLUE, alpha=0.85,
           edgecolor=SURFACE, linewidth=2, zorder=3)
for row in used.itertuples():
    ax.annotate(row.ticker, (row.unreal_loss_to_adj_equity, row.car_0_2),
                xytext=(7, 4), textcoords="offset points", fontsize=9, color=INK)

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

missing = ", ".join(sample.loc[sample["car_0_2"].isna(), "ticker"]) or "none"
ax.set_title(f"Securities losses vs. stock reaction to SVB's failure ({len(used)} banks)",
             color=INK, fontsize=11, loc="left")
fig.text(0.01, 0.01, f"Dot size = uninsured deposit share. Not shown (no returns yet): {missing}. "
         "Source: outputs/analysis_sample.csv", color=MUTED, fontsize=8)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "figures" / "scatter_loss_vs_car.png", dpi=200)

print(f"Regression on {int(fit.nobs)} banks (HC1 robust SEs):")
print(table[["term", "coef", "robust_se", "p_value"]].round(4).to_string(index=False))
print(f"R-squared: {fit.rsquared:.3f}")
print("Wrote outputs/regression_main.csv, regression_main.txt, figures/scatter_loss_vs_car.png")
