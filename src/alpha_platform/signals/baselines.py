import pandas as pd
import numpy as np


def equal_weight_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Baseline Strategy: Invests equally across all assets that have enough data.
    """
    out = df.copy()

    # Eligible if the 200-day SMA is available (avoids trading on Day 1)
    out['is_eligible'] = out['sma_ratio_20_200'].notna()

    # Count how many assets are eligible per day across the universe
    eligible_count = out.groupby('Date')['is_eligible'].transform('sum')

    # Assign 1/N weight to eligible assets
    out['target_weight'] = np.where(
        out['is_eligible'] & (eligible_count > 0),
        1.0 / eligible_count,
        0.0
    )
    return out


def trend_following_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Active Strategy: Only invests in assets exhibiting positive momentum (SMA ratio > 1.0).
    Moves to cash during downtrends.
    """
    out = df.copy()

    # The mathematical rule: Is the fast moving average > slow moving average?
    out['is_bullish'] = out['sma_ratio_20_200'] > 1.0

    # Count how many assets are bullish today
    bullish_count = out.groupby('Date')['is_bullish'].transform('sum')

    # Assign 1/N weight ONLY to bullish assets.
    # If 0 assets are bullish, we hold 100% cash (weights sum to 0).
    out['target_weight'] = np.where(
        out['is_bullish'] & (bullish_count > 0),
        1.0 / bullish_count,
        0.0
    )
    return out