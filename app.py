"""Bank fragility dashboard (Team Helble, Seed 6).

Run from the repo root:   streamlit run app.py

Reads ONLY from outputs/, so every number on screen traces to a file there.
Rebuild those files with the pipeline in code/ (see README.md) before presenting.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

OUT = Path(__file__).resolve().parent / "outputs"

st.set_page_config(page_title="Bank fragility: SVB and who's next", layout="wide")

# Load the three output files the dashboard needs.
sample = pd.read_csv(OUT / "analysis_sample.csv")
regression = pd.read_csv(OUT / "regression_main.csv")
scatter_png = OUT / "figures" / "scatter_loss_vs_car.png"

st.title("Bank fragility: SVB, and who's next")
st.caption("Team Helble · Fin 331 final project · v0 (12 banks)")

# All 12 banks have CRSP returns. If a rebuild ever leaves a CAR blank, say so loudly.
missing_car = sample.loc[sample["car_0_2"].isna(), "ticker"].tolist()
if missing_car:
    st.error(f"Missing car_0_2 for {', '.join(missing_car)}: rerun the pipeline (python run_all.py).")

intro, method, analysis, screen = st.tabs(
    ["Introduction", "Methodology", "Analysis", "Interactive fragility screen"])

# ---------------------------------------------------------------- Introduction
with intro:
    st.header("The question")
    st.write(
        "When Silicon Valley Bank failed on March 10, 2023, did listed banks with more "
        "**uninsured deposits** and larger **unrealized securities losses** suffer worse stock "
        "returns? And, using the same measures, which banks look most fragile?")
    st.write("**Who would use this:** bank supervisors (screening) and bank investors (risk screening).")

    # Headline numbers, straight from outputs/analysis_sample.csv.
    svb = sample[sample["ticker"] == "SIVB"].iloc[0]
    others = sample[sample["ticker"] != "SIVB"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Banks in v0 sample", len(sample))
    c2.metric("SVB uninsured deposit share", f"{svb['uninsured_dep_share']:.0%}",
              f"others: median {others['uninsured_dep_share'].median():.0%}", delta_color="off")
    c3.metric("SVB losses / adjusted equity", f"{svb['unreal_loss_to_adj_equity']:.0%}",
              f"others: median {others['unreal_loss_to_adj_equity'].median():.0%}", delta_color="off")
    st.caption("Source: outputs/analysis_sample.csv (call reports as of 12/31/2022).")

# ---------------------------------------------------------------- Methodology
with method:
    st.header("Data")
    st.markdown(
        "- **Bank balance sheets:** FFIEC Call Reports for **12/31/2022**, the last quarter before "
        "SVB failed (no look-ahead).\n"
        "- **Which banks belong to which company:** NY Fed CRSP-FRB link file and FFIEC NIC "
        "ownership data. Each holding company's bank subsidiaries are **summed first**, then the "
        "ratios are computed.\n"
        "- **Stock returns:** CRSP daily stock file via WRDS for all 12 banks and SPY "
        "(returns include dividends; delisting returns included where they apply). Banks are matched "
        "by CRSP PERMNO, not ticker, so delisted banks (SVB, Comerica) are included. "
        "Rebuilding needs a WRDS login; raw CRSP data is licensed and not shared.")

    st.header("Measures")
    st.markdown(
        "- **Uninsured deposit share** = estimated uninsured deposits / domestic deposits.\n"
        "- **Unrealized losses / adjusted equity (main)** = (HTM loss + AFS loss) / "
        "(total equity + AFS loss). AFS losses are already subtracted from book equity, so we "
        "add them back (Jiang, Matvos, Piskorski & Seru, 2023).\n"
        "- **HTM loss / equity (robustness)** = held-to-maturity loss / total equity.")

    st.header("Event study")
    st.markdown(
        "- **Market model:** each bank's daily return regressed on SPY's over calendar 2022.\n"
        "- **Abnormal return** = actual return − predicted return.\n"
        "- **CAR (days 0 to +2)** = sum of abnormal returns on Mar 9, 10 and 13, 2023. The window "
        "ends before the Credit Suisse shock on Mar 15.\n"
        "- SVB stopped trading after Mar 9 (halted Mar 10, then seized), so its CAR covers only "
        "Mar 9. CRSP's Mar 10 figure is a quote with no trade, so it is left out.")

    st.header("Regression")
    st.latex(r"CAR_i = a + b_1\,\text{uninsured share}_i + b_2\,\text{loss ratio}_i "
             r"+ b_3\,\log(\text{total assets}_i) + e_i")
    st.write("Heteroskedasticity-robust (HC1) standard errors.")

# ---------------------------------------------------------------- Analysis
with analysis:
    st.header("Regression results")
    n_obs = int(regression["n_obs"].iloc[0])
    st.write(f"{n_obs} banks: {regression['banks_used'].iloc[0]}. "
             f"R² = {regression['r_squared'].iloc[0]:.2f}.")
    st.dataframe(regression[["term", "coef", "robust_se", "p_value"]].round(4),
                 hide_index=True, width="content")
    st.info(f"With {n_obs} banks and 4 coefficients this is a pipeline check, not evidence.")
    st.caption("Source: outputs/regression_main.csv")

    st.header("Securities losses vs. stock reaction")
    st.image(str(scatter_png), width="stretch")
    st.caption("Source: outputs/figures/scatter_loss_vs_car.png")

# ---------------------------------------------------------------- Fragility screen
with screen:
    st.header("Interactive fragility screen")
    st.write("Filter and sort the v0 banks on their 12/31/2022 fragility measures.")

    # Filters: minimum uninsured share and minimum loss ratio.
    col1, col2 = st.columns(2)
    min_uninsured = col1.slider("Minimum uninsured deposit share", 0.0, 1.0, 0.0, 0.05)
    min_loss = col2.slider("Minimum losses / adjusted equity", 0.0, 1.0, 0.0, 0.05)

    # Sorting: pick a column and a direction.
    columns = {
        "Uninsured deposit share": "uninsured_dep_share",
        "Losses / adjusted equity": "unreal_loss_to_adj_equity",
        "HTM loss / equity": "htm_loss_to_equity",
        "CAR, days 0 to +2": "car_0_2",
        "Total assets ($ thousands)": "total_assets",
    }
    col3, col4 = st.columns(2)
    sort_label = col3.selectbox("Sort by", list(columns))
    descending = col4.radio("Order", ["Highest first", "Lowest first"], horizontal=True) == "Highest first"

    # Apply the filters and the sort, then show the table.
    shown = sample[(sample["uninsured_dep_share"] >= min_uninsured)
                   & (sample["unreal_loss_to_adj_equity"] >= min_loss)]
    shown = shown.sort_values(columns[sort_label], ascending=not descending)
    table = shown[["ticker", "bhc_name"] + list(columns.values())].rename(
        columns={v: k for k, v in columns.items()} | {"ticker": "Ticker", "bhc_name": "Holding company"})
    st.write(f"{len(shown)} of {len(sample)} banks match.")
    st.dataframe(table.round(3), hide_index=True, width="stretch")
    st.caption("Source: outputs/analysis_sample.csv. SIVB's CAR covers day 0 only.")
