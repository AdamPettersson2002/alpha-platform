# Alpha Platform

A reproducible, Python-based research stack for daily-data systematic trading strategies.

This project is built to demonstrate rigorous quantitative research discipline. Rather than focusing on finding a single "magic" backtest, this platform is engineered to emphasize correctness, reproducibility, and the strict prevention of data leakage. 

## Core Principles

1. **Reproducible Runs:** Completely config-driven (YAML) experiments with deterministic data cleaning and local Parquet caching.
2. **Strict Timing (No Leakage):** Architectural guarantees that models never see future data. The platform explicitly enforces that signals computed from day T are executed at day T+1.
3. **Tradability First:** Realistic transaction cost modeling (bps based on turnover) and portfolio constraints (max weights, volatility targeting) to ensure strategies survive realistic market frictions.
4. **Honest Evaluation:** Machine learning models are strictly evaluated using walk-forward (rolling/expanding) windows and must compete against simple baselines (Equal-Weight, Trend) after costs.

---

## System Architecture

The platform is designed as a strict, unidirectional pipeline:

1. **Data Layer:** Configurable ingestion of daily OHLCV data. Enforces a common calendar index and strictly uses forward-filling for missing data to prevent look-ahead bias. Data is cached locally as Parquet.
2. **Feature Pipeline:** Computes cross-sectional and time-series features (returns, volatility, trend). Enforces strict shifting rules so that predictive models only access past information.
3. **Signals & Models:** Contains baseline rule-based signals and optional walk-forward tabular machine learning models. Generates a daily matrix of Target Weights.
4. **Portfolio Construction:** Translates raw signals into risk-managed target weights, applying exposure caps and turnover control.
5. **Backtest Engine:** A walk-forward simulation that steps through time, applies transaction costs based on portfolio turnover, and produces net return series.
6. **Reporting:** Generates standardized artifacts (HTML/PDF/Jupyter Tearsheets) comparing the strategy's risk-adjusted performance (Sharpe, Max Drawdown) against baselines.

---

## Current Status

The underlying infrastructure (M1-M4) is strictly functional. The project is currently transitioning from Infrastructure Engineering to Alpha Research (M6+).

- [x] **M1: Foundation** - Package architecture (`src/` layout), CLI scaffolding, linting, testing, and CI/CD pipelines.
- [x] **M2: Data Layer** - Defensive data ingestion via `yfinance`, calendar alignment, missingness tracking, and immutable Parquet dataset generation.
- [x] **M3: Feature Pipeline** - Implementation of strictly-timed feature transformations (returns, volatility, trend) backed by mathematical leakage tests.
- [x] **M4: Backtest Engine** - Wide-Matrix Iterative simulation loop with realistic state-tracking, turnover calculation, and transaction costs.
- [x] **M5: Signals & Baselines** - Decoupling the "Brain" (Signal Generation) from the "Engine" (Execution). Implemented Equal-Weight and Trend-Following A/B testing.
- [ ] *M6: Alpha Research & Machine Learning (Next)* - Shifting to the Quant Researcher role. Testing walk-forward ML models (Linear/Tree-based) against stationary features to predict forward returns.

---

## Feature Engineering (M3)

The feature pipeline transforms raw pricing data into stationary, predictive signals and risk metrics. To strictly prevent look-ahead bias, the platform enforces a mathematical shifting rule: any feature calculated using data up to day $t$ is strictly shifted to day $t+1$.

### 1. Log Returns

$$
R_{t, N} = \ln\left(\frac{P_t}{P_{t-N}}\right)
$$

### 2. Trend Feature (SMA Ratio)

$$
\text{Trend}_t = \frac{\frac{1}{S} \sum_{i=0}^{S-1} P_{t-i}}{\frac{1}{L} \sum_{i=0}^{L-1} P_{t-i}}
$$

### 3. Risk Feature (Rolling Volatility)

$$
\sigma_{t, W} = \sqrt{\frac{1}{W-1} \sum_{i=0}^{W-1} (R_{t-i, 1} - \bar{R})^2}
$$

---

## Backtest Engine Mechanics (M4 & M5)

The platform utilizes a **Wide-Matrix Iterative** state machine. Rather than using simplified vector math, it explicitly loops through time $t$, tracking physical state variables (Cash, Shares Held) to enforce path-dependency and realistic trading frictions.

Let $N$ be the number of assets in the universe. At the beginning of day $t$, we observe closing prices $P_{i,t}$ and receive target weights $w_{i,t}$ from the Signal layer.

### 1. Mark-to-Market (Total Equity)
The total portfolio value $V_t$ is the sum of uninvested cash and the current market value of all shares held from the previous day ($h_{i,t-1}$).

$$
V_t = C_{t-1} + \sum_{i=1}^{N} \left( h_{i,t-1} \times P_{i,t} \right)
$$

### 2. Target Execution
The engine calculates the new target shares $h^*_{i,t}$ required to satisfy the Signal layer's requested weights.

$$
h^*_{i,t} = \frac{w_{i,t} \times V_t}{P_{i,t}}
$$

### 3. Turnover & Transaction Costs
Turnover is physically calculated as the absolute difference between the newly requested shares and the current shares held. A cost rate $c$ (e.g., $5$ bps, or $0.0005$) is applied to the gross traded value.

$$
\text{Costs}_t = c \times \sum_{i=1}^{N} \left| \left(h^*_{i,t} - h_{i,t-1}\right) \times P_{i,t} \right|
$$

### 4. State Update (Path Dependency)
Cash is adjusted by subtracting the capital required for net purchases and the frictional transaction costs. The engine then steps forward to $t+1$.

$$
C_t = C_{t-1} - \sum_{i=1}^{N} \left( \left(h^*_{i,t} - h_{i,t-1}\right) \times P_{i,t} \right) - \text{Costs}_t
$$

---
*Disclaimer: Educational research code. Not investment advice.*