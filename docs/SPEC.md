# Specification — Alpha Platform (Daily Data)

This document defines what the platform is supposed to do and the assumptions it makes.
It is a living spec; update it when behavior changes.

---

## 1. Purpose

Alpha Platform is a reproducible research stack for daily-data systematic strategies.

It aims to answer:
> Does a signal or model produce a risk-managed, tradable strategy that generalizes out-of-sample?

The emphasis is on correctness and research discipline, not on “best backtest”.

---

## 2. System Overview (Pipeline)

1. **Data**
   - Download daily OHLCV for a configurable universe (ETFs initially)
   - Clean and align on a common calendar
   - Store locally as Parquet for reproducibility

2. **Features**
   - Compute features from past information only
   - Enforce strict feature timing (no leakage)

3. **Signals / Models**
   - Baseline rule-based signals (trend, simple rules)
   - Optional ML models (tabular models; walk-forward training)

4. **Portfolio + Risk**
   - Convert signals into weights with constraints
   - Volatility targeting and exposure limits
   - Turnover control

5. **Backtesting**
   - Walk-forward simulation with rebalancing schedule
   - Transaction costs applied based on turnover
   - Produce daily returns series + metrics

6. **Evaluation + Reporting**
   - Compare to baselines
   - Robustness checks (costs, windows, rebalance frequency)
   - Generate a standardized report artifact

---

## 3. Timing Conventions (No Leakage)

This is the most important part of the spec.

### 3.1 Information Availability
Assume:
- The **close** price for day *t* is known **at the end of day t**.
- Any features computed using day *t* close are available for trading **from day t+1 onward**.

Therefore:
- If a strategy generates signals at end of day *t*, it enters positions at the next rebalance time (e.g., open or close of day t+1 depending on implementation).
- For daily data simplicity, default assumption:
  - **signals computed from day t are executed at day t+1 close** (or next rebalance date close)
  - This avoids pretending you can trade at the same close you used to compute the signal.

(If you change execution assumptions later, update this section and the backtester.)

### 3.2 Feature Shifting Rule
All features intended to predict returns over [t+1 … t+h] must be computed from data ≤ t, and then shifted so the model never sees future.

Example:
- `momentum_20[t]` computed from prices up to t
- used to decide position held during t+1

### 3.3 Common Leakage Pitfalls
- Using forward-filled values across long gaps
- Using rolling statistics without shifting the final value
- Using next-day returns inside training features accidentally
- Training/testing splits that allow overlapping label windows

Platform requirement: timing assumptions must be encoded and tested.

---

## 4. Data Specification

### 4.1 Source
Initial implementation uses `yfinance` for daily OHLCV.

### 4.2 Stored Dataset Format (recommended)
Store either:
- one Parquet per ticker (simple) OR
- a single Parquet with multi-index columns (ticker × field)

In either case, include:
- Open, High, Low, Close, Adj Close (if used), Volume
- Common calendar index
- Clear metadata snapshot (start/end, missingness)

### 4.3 Cleaning / Alignment Rules
- Align all assets on a common date index
- Handle missing values:
  - drop assets with insufficient history/coverage
  - optionally forward-fill small gaps (document thresholds)
- Log warnings for:
  - short histories
  - large missing segments
  - suspicious outliers (optional)

---

## 5. Feature Specification (MVP)

Minimum feature set:
- Returns: 1D, 5D, 20D log returns
- Volatility: rolling std of returns (e.g., 20D)
- Trend: moving average ratio or time-series momentum (e.g., 12M-1M style possible on daily)
- Volume: rolling mean / z-score (optional for ETFs)

All features must follow timing rules.

---

## 6. Signals / Strategies

### 6.1 Baselines (required)
- Equal-weight buy & hold
- Vol-targeted equal-weight
- Simple trend (time-series momentum)

### 6.2 Main Strategy (choose one initially)
Option A: Trend ensemble
- multiple lookbacks
- combine into a score
- risk overlay (vol scaling)

Option B: ML forecasting
- tabular model (regularized linear / GBM)
- walk-forward retraining
- optional quantile forecasts

### 6.3 ML Policy
ML is only acceptable if:
- evaluated walk-forward
- compared to baselines after costs
- reported honestly if it does not help

---

## 7. Portfolio Construction / Risk

### 7.1 Position sizing (MVP)
- Convert scores to weights
- Scale by inverse volatility or vol targeting
- Apply constraints:
  - max weight per asset
  - leverage cap (if used)
  - optional minimum weight threshold

### 7.2 Turnover control
- Penalize large changes in weights
- Apply a turnover cap or smoothing

---

## 8. Transaction Costs Model (MVP)

Model transaction costs as:
- `cost[t] = cost_bps * turnover[t]`
where turnover is sum of absolute weight changes (or dollar turnover).
Document chosen definition.

Report:
- gross returns
- net returns (after costs)
- turnover series and average turnover

---

## 9. Backtest Specification

Backtester must:
- support rebalancing frequency (weekly/monthly)
- simulate holdings and apply costs at trades
- produce:
  - daily net returns
  - equity curve
  - drawdowns
  - exposure summary
  - turnover

---

## 10. Reporting Specification

Minimum report content:
- equity curve
- drawdown curve
- summary metrics table (CAGR, vol, Sharpe, max DD, turnover)
- comparison vs baselines
- at least one robustness table (cost sensitivity)

---

## 11. CLI Specification (planned)

- `download --config configs/universe.yaml`
- `features --config configs/features.yaml` (optional)
- `backtest --config configs/experiment.yaml`
- `report --run-id <id>`

Each command must be deterministic given configs and cached data.

---

## 12. Disclaimer
Educational research code. Not investment advice.
