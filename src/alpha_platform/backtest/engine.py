import pandas as pd
from rich.console import Console

console = Console()


def prepare_wide_matrices(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Pivots long-format data into wide matrices (Dates x Tickers) for the iterative loop.
    Also generates a simple Equal-Weight baseline target weight matrix.
    """
    # Pivot Close prices
    prices = df.pivot(index='Date', columns='Ticker', values='Close').ffill()

    # Generate Equal-Weight Target Weights (Baseline)
    # We only invest in assets that have surpassed their NaN window (e.g., 200 days for trend)
    is_eligible = df.pivot(index='Date', columns='Ticker', values='sma_ratio_20_200').notna()

    # Count eligible assets per day (sum across rows)
    eligible_count = is_eligible.sum(axis=1)

    # 1/N weights where eligible, 0 otherwise
    target_weights = is_eligible.div(eligible_count, axis=0).fillna(0.0)

    return prices, target_weights


def run_iterative_backtest(df: pd.DataFrame, initial_capital: float = 100_000.0, cost_bps: float = 5.0) -> pd.DataFrame:
    """
    Runs a Wide-Matrix Iterative backtest.
    Strictly steps through time to accurately model compounding and transaction costs.
    """
    prices, target_weights = prepare_wide_matrices(df)
    dates = prices.index
    tickers = prices.columns

    # --- Initialize State Variables ---
    cash = initial_capital
    shares_held = pd.Series(0.0, index=tickers)

    # --- Tracking Arrays ---
    history_portfolio_value = []
    history_turnover_pct = []

    cost_rate = cost_bps / 10000.0

    console.print(f"Starting iteration over {len(dates)} trading days...")

    # --- The Core Iterative Loop ---
    for t in range(len(dates)):
        current_date = dates[t]
        current_prices = prices.iloc[t].fillna(0.0)

        # 1. Mark-to-Market (What are we worth today?)
        holdings_value = (shares_held * current_prices).sum()
        portfolio_value = cash + holdings_value

        # 2. Get today's target weights
        # Note: Because features were shifted in M3, target_weights.iloc[t]
        # only contains information computed up to day t-1. No leakage!
        w_target = target_weights.iloc[t]

        # 3. Calculate target capital allocation per asset
        target_capital = w_target * portfolio_value

        # 4. Calculate target shares (assuming fractional shares for MVP)
        # Avoid division by zero if an asset price is missing (0.0)
        target_shares = target_capital.copy()
        valid_prices = current_prices > 0
        target_shares[valid_prices] = target_capital[valid_prices] / current_prices[valid_prices]
        target_shares[~valid_prices] = 0.0

        # 5. Calculate Trades (Delta Shares)
        trades_shares = target_shares - shares_held
        trades_capital = trades_shares * current_prices

        # 6. Calculate Turnover and Costs
        traded_value = trades_capital.abs().sum()
        costs = traded_value * cost_rate

        # Calculate daily turnover as % of portfolio for reporting
        turnover_pct = (traded_value / portfolio_value) if portfolio_value > 0 else 0.0

        # 7. Update State for Tomorrow
        cash = cash - trades_capital.sum() - costs
        shares_held = target_shares

        # 8. Record end-of-day stats
        # We record the value *after* paying costs to accurately reflect net equity
        end_of_day_value = cash + (shares_held * current_prices).sum()

        history_portfolio_value.append(end_of_day_value)
        history_turnover_pct.append(turnover_pct)

    # --- Post-Processing Results ---
    results = pd.DataFrame({
        'Date': dates,
        'equity': history_portfolio_value,
        'turnover': history_turnover_pct
    }).set_index('Date')

    # Calculate daily net returns from the equity curve
    results['net_ret'] = results['equity'].pct_change().fillna(0.0)
    results['cumulative_net'] = results['equity'] / initial_capital

    return results