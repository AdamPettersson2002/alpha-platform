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
3. **Signals & Models:** Contains baseline rule-based signals and optional walk-forward tabular machine learning models.
4. **Portfolio Construction:** Translates raw signals into risk-managed target weights, applying exposure caps and turnover control.
5. **Backtest Engine:** A walk-forward simulation that steps through time, applies transaction costs based on portfolio turnover, and produces net return series.
6. **Reporting:** Generates standardized artifacts (HTML/PDF) comparing the strategy's risk-adjusted performance (Sharpe, Max Drawdown) against baselines, alongside robustness checks.

---

## Current Status

The platform is currently under active development, adhering to a strict milestone-driven roadmap.

- [x] **M1: Foundation** - Package architecture (`src/` layout), CLI scaffolding, linting, testing, and CI/CD pipelines.
- [x] **M2: Data Layer** - Defensive data ingestion via `yfinance`, calendar alignment, missingness tracking, and immutable Parquet dataset generation.
- [ ] *M3: Feature Pipeline (Next)* - Implementation of strictly-timed feature transformations (returns, volatility, trend).
- [ ] *M4: Backtest Engine v1* - Core simulation loop, holdings update logic, and transaction cost modeling.

---
*Disclaimer: Educational research code. Not investment advice.*