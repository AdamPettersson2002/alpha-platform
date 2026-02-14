import pandas as pd
import numpy as np
from alpha_platform.features.builder import build_features


def test_feature_shifting_prevents_leakage():
    """
    Proves that features available on Day T only contain data from Day T-1 and earlier.
    """
    # 1. ARRANGE: Create synthetic price data
    dates = pd.date_range(start="2026-01-01", periods=4)

    # Asset A doubles, stays flat, doubles
    df_a = pd.DataFrame({
        "Date": dates,
        "Ticker": "AAA",
        "Open": [10.0, 20.0, 20.0, 40.0],
        "High": [10.0, 20.0, 20.0, 40.0],
        "Low": [10.0, 20.0, 20.0, 40.0],
        "Close": [10.0, 20.0, 20.0, 40.0],
        "Adj Close": [10.0, 20.0, 20.0, 40.0],
        "Volume": [100, 100, 100, 100]
    })

    # Asset B loses half, stays flat, loses half
    df_b = pd.DataFrame({
        "Date": dates,
        "Ticker": "BBB",
        "Close": [100.0, 50.0, 50.0, 25.0],
        "Open": [100.0, 50.0, 50.0, 25.0],
        "High": [100.0, 50.0, 50.0, 25.0],
        "Low": [100.0, 50.0, 50.0, 25.0],
        "Adj Close": [100.0, 50.0, 50.0, 25.0],
        "Volume": [100, 100, 100, 100]
    })

    raw_df = pd.concat([df_a, df_b], ignore_index=True)

    # 2. ACT: Run the feature builder
    features_df = build_features(raw_df)

    # Extract Asset A's results to verify the math
    a_results = features_df[features_df['Ticker'] == 'AAA'].reset_index(drop=True)

    # 3. ASSERT: The Golden Rule of Timing

    # Day 1 (Index 0): No past data exists. Shifted feature must be NaN.
    assert pd.isna(a_results.loc[0, 'return_1d'])

    # Day 2 (Index 1): The raw return for Day 1 was NaN.
    # Shifted feature on Day 2 must also be NaN.
    assert pd.isna(a_results.loc[1, 'return_1d'])

    # Day 3 (Index 2): The raw return on Day 2 was ln(20/10) = ln(2).
    # The feature available on Day 3 MUST be Day 2's return.
    expected_ln_2 = np.log(2.0)
    actual_day_3_feature = a_results.loc[2, 'return_1d']
    assert np.isclose(actual_day_3_feature, expected_ln_2), \
        f"Leakage detected! Expected {expected_ln_2}, got {actual_day_3_feature}"

    # Day 4 (Index 3): The raw return on Day 3 was ln(20/20) = 0.
    # The feature available on Day 4 MUST be Day 3's return.
    expected_zero = 0.0
    actual_day_4_feature = a_results.loc[3, 'return_1d']
    assert np.isclose(actual_day_4_feature, expected_zero), \
        f"Leakage detected! Expected {expected_zero}, got {actual_day_4_feature}"


def test_cross_sectional_isolation():
    """
    Proves that moving averages and returns do not bleed across different tickers.
    """
    # Reusing the exact same setup from above
    dates = pd.date_range(start="2026-01-01", periods=2)
    df_a = pd.DataFrame(
        {"Date": dates, "Ticker": "AAA", "Close": [10.0, 20.0], "Open": [10.0, 20.0], "High": [10.0, 20.0],
         "Low": [10.0, 20.0], "Adj Close": [10.0, 20.0], "Volume": [100, 100]})
    df_b = pd.DataFrame(
        {"Date": dates, "Ticker": "BBB", "Close": [100.0, 50.0], "Open": [100.0, 50.0], "High": [100.0, 50.0],
         "Low": [100.0, 50.0], "Adj Close": [100.0, 50.0], "Volume": [100, 100]})
    raw_df = pd.concat([df_a, df_b], ignore_index=True)

    features_df = build_features(raw_df)

    b_results = features_df[features_df['Ticker'] == 'BBB'].reset_index(drop=True)

    # Asset B went from 100 -> 50. The raw return is ln(0.5).
    # This return should appear on Day 3 for Asset B (if we had a Day 3).
    # But crucially, we must ensure Asset B's Day 2 feature isn't poisoned by Asset A's prices.
    assert pd.isna(b_results.loc[1, 'return_1d']), "Cross-sectional leak! Asset A's data bled into Asset B."