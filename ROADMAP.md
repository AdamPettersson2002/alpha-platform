# Roadmap — Alpha Platform (Daily Data)

This roadmap is a living plan for building a reproducible daily-data systematic trading research platform:
**data → features → signals/models → portfolio+risk → backtest with costs → evaluation → report**

The project is designed to demonstrate real quant/ML research discipline:
- no leakage (strict timing)
- walk-forward evaluation
- strong baselines
- transaction costs + turnover
- robustness checks
- reproducible runs via configs

---

## Project Principles (Non-negotiable)

1. **Reproducible runs**
   - Config-driven experiments (YAML)
   - Cached datasets stored as Parquet
   - Deterministic cleaning and feature generation

2. **Correct evaluation**
   - Walk-forward testing only (rolling/expanding windows)
   - Explicit timing assumptions documented and tested
   - No leakage (no future info in training/features)

3. **Baselines first**
   - Buy & hold / equal weight
   - Vol-targeted baseline
   - Simple trend baseline (or other simple rule-based baseline)

4. **Tradability**
   - Transaction costs modeled and reported
   - Turnover tracked and reported
   - Position/risk constraints applied (max weights, vol targeting)

5. **Communication**
   - Standardized report output
   - Honest limitations + failure analysis

---

## Definitions of Done (Global)

A module is “done” when:
- It has clear inputs/outputs and assumptions documented.
- It has at least minimal tests (unit tests where possible).
- It’s wired into the CLI (if appropriate).
- It’s reproducible (running the same command twice gives the same artifact).
- It produces a clear summary log / output.

---

## Milestones (Weekend Pace)

### M1 — Repo Foundation (Done when CI + packaging + minimal CLI work)
- [ ] Package structure under `src/alpha_platform/`
- [ ] `pyproject.toml` with dependencies + dev deps
- [ ] Ruff + Pytest + GitHub Actions CI
- [ ] Minimal CLI works: `python -m alpha_platform.cli --help`

**Definition of done:** `pip install -e ".[dev]"` works, CI passes, CLI runs.

---

### M2 — Data Ingestion & Dataset Build (Download → Clean → Parquet)
Implement:
- CLI: `download --config configs/universe.yaml`
- Data alignment (calendar), missingness summary, warnings
- Local storage: Parquet + metadata snapshot

**Tasks**
- [ ] Create `configs/universe.yaml` (tickers, start/end date)
- [ ] Implement downloader + caching
- [ ] Implement cleaning + alignment
- [ ] Write Parquet dataset
- [ ] Print summary stats (coverage, missingness, start/end)
- [ ] Tests (mock download; no network)

**Definition of done:** running download produces a deterministic dataset and summary.

---

### M3 — Feature Pipeline (Strict Timing)
Implement:
- Returns, rolling volatility, trend features, simple volume features
- A clear timing convention (documented + tested)

**Tasks**
- [ ] Implement `features.build_features(...)`
- [ ] Ensure all features are shifted correctly for tradable signals
- [ ] Feature unit tests with tiny synthetic data

**Definition of done:** features are correct, documented, and provably no-leakage.

---

### M4 — Backtester v1 (Holdings, Rebalance, Costs)
Implement:
- Rebalancing schedule (weekly/monthly default)
- Portfolio holdings update logic
- Transaction costs and turnover computation
- Metrics: daily returns, cumulative, drawdown, turnover

**Tasks**
- [ ] Implement backtest engine
- [ ] Implement cost model (bps * turnover)
- [ ] Implement portfolio accounting + sanity checks

**Definition of done:** can run end-to-end on one simple baseline strategy.

---

### M5 — Baselines + First Report
Implement baseline strategies:
- Equal weight / buy-and-hold
- Vol targeting baseline
- Simple trend baseline (time-series momentum)

Reporting v1:
- Cumulative returns, drawdowns
- Sharpe/Sortino (with caveats)
- Max DD, turnover, exposure summary

**Definition of done:** one command runs a baseline backtest and outputs a report artifact.

---

### M6 — Main Signal Approach (Choose One Path)
Pick one “main” approach:
- **A: Trend ensemble** (multiple lookbacks + risk overlay)
- **B: ML forecasting** (tabular model; optional quantile forecast)

**Definition of done:** main approach runs walk-forward and is compared to baselines.

---

### M7 — Portfolio Constraints Layer
Add:
- max weight per asset
- leverage cap (if needed)
- turnover cap or penalty
- optional optimizer (mean-variance or CVaR) as stretch

**Definition of done:** constraints work and are reflected in turnover and risk.

---

### M8 — Robustness + Ablations
Add:
- cost sensitivity (e.g., 5/10/20 bps)
- rebalance sensitivity (weekly vs monthly)
- train window sensitivity (if ML)
- ablations (remove features/signal components)

**Definition of done:** report includes a small robustness table.

---

### M9 — Report v2 + Research Memo
Output:
- cleaner report
- 1–2 page “research memo” summarizing hypothesis, method, results, limitations, next steps

**Definition of done:** someone unfamiliar can read and understand the project quickly.

---

### M10 — Polish for Screening
- [ ] Clean README (how to reproduce)
- [ ] Reduce notebooks to 1–2 max
- [ ] Improve tests (core correctness)
- [ ] Ensure CI fully green
- [ ] Tags/releases optional

**Definition of done:** repo looks professional, reproducible, and defensible in interviews.

---

## Current Focus
- Current milestone: **M2 — Data Ingestion & Dataset Build**
- Next deliverable: `download` command + Parquet dataset + missingness summary

---

## Notes / Parking Lot
Use this section to park ideas so the scope doesn’t explode:
- [ ] Add macro data (FRED) features
- [ ] Add probabilistic/quantile forecasting
- [ ] Add optimizer (CVaR)
- [ ] Add Streamlit dashboard
