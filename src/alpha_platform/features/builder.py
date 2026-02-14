import pandas as pd
import numpy as np


def compute_log_returns(df: pd.DataFrame, periods: list[int] = [1, 5, 20]) -> pd.DataFrame:
    """
    Computes backward-looking rolling log returns.
    """
    out = df.copy()
    for p in periods:
        # We MUST group by Ticker so SPY's prices don't bleed into QQQ's prices
        out[f'return_{p}d'] = out.groupby('Ticker')['Close'].transform(
            lambda x: np.log(x / x.shift(p))
        )
    return out


def compute_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Computes rolling standard deviation of 1-day log returns (Volatility).
    """
    out = df.copy()
    # Ensure 1D returns exist to calculate volatility
    if 'return_1d' not in out.columns:
        out = compute_log_returns(out, periods=[1])

    out[f'volatility_{window}d'] = out.groupby('Ticker')['return_1d'].transform(
        lambda x: x.rolling(window=window).std()
    )
    return out


def compute_trend(df: pd.DataFrame, short_window: int = 20, long_window: int = 200) -> pd.DataFrame:
    """
    Computes a simple Trend feature: the ratio of a fast moving average to a slow one.
    Values > 1 indicate an uptrend.
    """
    out = df.copy()
    sma_short = out.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=short_window).mean())
    sma_long = out.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=long_window).mean())

    out[f'sma_ratio_{short_window}_{long_window}'] = sma_short / sma_long
    return out


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master function to compute all features and strictly enforce timing rules.
    """
    # 1. Sort chronologically per asset (Critical for accurate rolling windows)
    df = df.sort_values(['Ticker', 'Date']).copy()

    # 2. Compute all raw features at time T
    df = compute_log_returns(df, periods=[1, 5, 20])
    df = compute_volatility(df, window=20)
    df = compute_trend(df, short_window=20, long_window=200)

    # 3. THE STRICT TIMING SHIFT (No-Leakage Guarantee)
    # Identify all the newly created feature columns
    base_cols = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    feature_cols = [col for col in df.columns if col not in base_cols]

    # Shift all features forward by exactly 1 row within each Ticker group.
    # What was calculated at the Close of Day T is now only available on Day T+1.
    df[feature_cols] = df.groupby('Ticker')[feature_cols].shift(1)

    return df