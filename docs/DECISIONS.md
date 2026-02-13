# Decisions Log — Alpha Platform

A lightweight log of key decisions and why they were made.
Update this whenever you make a change that affects assumptions, reproducibility, or evaluation.

---

## 2026-02-13 — Project Setup
**Decision:** Use a `src/` layout (`src/alpha_platform/...`).  
**Why:** Prevents import confusion and matches professional packaging practices.

**Decision:** Daily data first (ETFs)  
**Why:** Easier reproducibility, fewer survivorship issues, lower complexity than intraday.

---

## Data
**Decision:** Use yfinance initially  
**Why:** Simple and accessible for daily OHLCV; good enough for a portfolio project.

**Decision:** Store data as Parquet under `data/` (gitignored)  
**Why:** Fast, reproducible, keeps repo clean.

(Record here whether you choose “one parquet per ticker” or “single multi-index parquet”.)

---

## Timing / No Leakage
**Decision:** Signals computed using day t data are executed starting day t+1  
**Why:** Avoids unrealistic “trade the close you just used”.

(If you later assume open execution or next-day close, record it here and update SPEC.md.)

---

## Backtesting / Costs
**Decision:** Transaction costs modeled as bps × turnover  
**Why:** Simple, transparent, and forces realism early.

(Record the chosen default bps value and why.)

---

## Modeling
**Decision:** Baselines required before ML  
**Why:** Prevents overfitting and ensures ML adds value vs simple rules.

**Decision:** Prefer stable tabular models for daily data  
**Why:** Lower risk of overfitting; easier to validate and explain.

---

## Reporting
**Decision:** Standard report artifact (HTML/PDF) generated per run  
**Why:** Makes results shareable, repeatable, and interview-friendly.

---

## Notes
Add future decisions here as you go:
- optimizer choice (mean-variance vs CVaR)
- rebalance frequency defaults
- feature set changes
- robustness methodology changes
