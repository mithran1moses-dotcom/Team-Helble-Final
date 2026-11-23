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

# Load the output files the dashboard needs. LATEST names the newest call-report
# quarter built by code/02 (outputs/bhc_measures_<LATEST>.csv) for the "today" screen.
LATEST = "2026Q3"
sample = pd.read_csv(OUT / "analysis_sample.csv")
latest = pd.read_csv(OUT / f"bhc_measures_{LATEST}.csv")
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
    st.write("Heteroskedasticity-robust (HC3) standard errors with t-based p-values "
             "(better behaved than HC1 and normal p-values at small N). Banks that failed "
             "inside the event window (SVB) are left out: their collapse is the shock, not a "
             "reaction to it. The version with SVB is kept as a robustness check.")

# ---------------------------------------------------------------- Analysis
with analysis:
    st.header("Regression results")
    n_obs = int(regression["n_obs"].iloc[0])
    st.write(f"{n_obs} banks: {regression['banks_used'].iloc[0]}. "
             f"R² = {regression['r_squared'].iloc[0]:.2f}.")
    st.dataframe(regression[["term", "coef", "robust_se", "t_stat", "p_value"]].round(4),
                 hide_index=True, width="content")
    st.info(f"With {n_obs} banks and 4 coefficients this is a pipeline check, not evidence.")
    st.caption("Source: outputs/regression_main.csv (failed banks excluded; HC3, t p-values)")

    st.subheader("Robustness: with SVB put back in")
    with_failed = pd.read_csv(OUT / "regression_with_failed.csv")
    st.dataframe(with_failed[["term", "coef", "robust_se", "t_stat", "p_value"]].round(4),
                 hide_index=True, width="content")
    st.caption(f"{int(with_failed['n_obs'].iloc[0])} banks. "
               "Source: outputs/regression_with_failed.csv")

    st.header("Securities losses vs. stock reaction")
    st.image(str(scatter_png), width="stretch")
    st.caption("Source: outputs/figures/scatter_loss_vs_car.png")

# ---------------------------------------------------------------- Fragility screen
with screen:
    st.header("Interactive fragility screen")

    # Pick the quarter. "Today" = the latest call reports; the event quarter
    # (12/31/2022) also shows each bank's CAR. The report date is read from the
    # file's report_period column (e.g. 09302026 -> 09/30/2026).
    def report_date(df):
        period = str(df["report_period"].iloc[0]).zfill(8)  # read as a number: put back the leading 0
        return f"{period[:2]}/{period[2:4]}/{period[4:]}"
    latest_label = f"Today: latest call reports ({report_date(latest)})"
    event_label = f"Before SVB failed ({report_date(sample)}), with CAR"
    quarter = st.radio("Quarter", [latest_label, event_label], horizontal=True)
    if quarter == latest_label:
        data, source = latest, f"outputs/bhc_measures_{LATEST}.csv"
        gone = sorted(set(sample["ticker"]) - set(latest["ticker"]))
        st.write(f"Fragility measures from the **{report_date(latest)}** call reports.")
        st.caption(f"Not shown, no longer independent filers: {', '.join(gone)}. SIVB failed "
                   "(Mar 10, 2023); Comerica (CMA) merged into Fifth Third (FITB) in Feb 2026, so "
                   "FITB's numbers now include Comerica. Banks are linked to holding companies as "
                   "of 12/31/2022; subsidiaries added since are not captured.")
    else:
        data, source = sample, "outputs/analysis_sample.csv"
        st.write(f"Fragility measures from the **{report_date(sample)}** call reports, "
                 "the last before SVB failed, next to each bank's stock reaction.")

    # Filters: minimum uninsured share and minimum loss ratio.
    col1, col2 = st.columns(2)
    min_uninsured = col1.slider("Minimum uninsured deposit share", 0.0, 1.0, 0.0, 0.05)
    min_loss = col2.slider("Minimum losses / adjusted equity", 0.0, 1.0, 0.0, 0.05)

    # Sorting: pick a column and a direction.
    columns = {
        "Uninsured deposit share": "uninsured_dep_share",
        "Losses / adjusted equity": "unreal_loss_to_adj_equity",
        "HTM loss / equity": "htm_loss_to_equity",
        "Total assets ($ thousands)": "total_assets",
    }
    if quarter == event_label:
        columns["CAR, days 0 to +2"] = "car_0_2"  # CARs exist only for the event
    col3, col4 = st.columns(2)
    sort_label = col3.selectbox("Sort by", list(columns))
    descending = col4.radio("Order", ["Highest first", "Lowest first"], horizontal=True) == "Highest first"

    # Apply the filters and the sort, then show the table.
    shown = data[(data["uninsured_dep_share"] >= min_uninsured)
                 & (data["unreal_loss_to_adj_equity"] >= min_loss)]
    shown = shown.sort_values(columns[sort_label], ascending=not descending)
    table = shown[["ticker", "bhc_name"] + list(columns.values())].rename(
        columns={v: k for k, v in columns.items()} | {"ticker": "Ticker", "bhc_name": "Holding company"})
    st.write(f"{len(shown)} of {len(data)} banks match.")
    st.dataframe(table.round(3), hide_index=True, width="stretch")
    note = " SIVB's CAR covers day 0 only." if quarter == event_label else ""
    st.caption(f"Source: {source}.{note}")
