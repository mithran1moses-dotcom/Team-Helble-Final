# Specs tried

Every regression or chart spec we run gets one row here, including the ones we drop.
Add the date and your name. The output file is where the numbers live (always in `outputs/`).

| # | Date | Who | Dependent variable | Regressors | Sample | Std. errors | Output file | Result / why kept or dropped |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-07 | Mithran (Claude Code) | `car_0_2` | `uninsured_dep_share`, `unreal_loss_to_adj_equity`, `log_total_assets` | v0, 10 of 12 banks (SIVB, CMA missing returns until CRSP arrives) | HC1 robust | `outputs/regression_main.csv`, `outputs/regression_main.txt` | Pipeline check only (N=10, 4 coefficients). Loss ratio coef −0.23 (p=0.53), uninsured share −0.97 (p=0.27), log assets +0.13 (p<0.01), R² 0.72. Kept as main spec; re-run when CRSP returns are added. |
| 2 | 2026-11-07 | Mithran (Claude Code) | `car_0_2` (chart) | x = `unreal_loss_to_adj_equity`, dot size = `uninsured_dep_share` | same 10 banks | n/a | `outputs/figures/scatter_loss_vs_car.png` | Headline scatter. Superseded by #4. |
| 3 | 2026-11-09 | Mithran (Claude Code) | `car_0_2` | `uninsured_dep_share`, `unreal_loss_to_adj_equity`, `log_total_assets` | v0, all 12 banks; returns from CRSP via WRDS (matched by PERMNO); SIVB's CAR covers day 0 only | HC1 robust | `outputs/regression_main.csv`, `outputs/regression_main.txt` | Same spec as #1, now N=12. Loss ratio coef −0.05 (p=0.87), uninsured share −0.44 (p=0.23), log assets +0.12 (p<0.01), R² 0.73. Kept as main spec. Pipeline check only: 12 banks, 4 coefficients. #1 (10 banks, yfinance) is kept above for comparison; its output files were overwritten by this run. |
| 4 | 2026-11-09 | Mithran (Claude Code) | `car_0_2` (chart) | x = `unreal_loss_to_adj_equity`, dot size = `uninsured_dep_share` | same 12 banks as #3 | n/a | `outputs/figures/scatter_loss_vs_car.png` | Headline scatter with SIVB and CMA added. Kept. |
