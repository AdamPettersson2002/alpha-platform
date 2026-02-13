import pandas as pd
from unittest.mock import patch
from alpha_platform.data.ingestion import download_and_clean_data


@patch("alpha_platform.data.ingestion.yf.download")
def test_download_and_clean_data_success(mock_download):
    """
    Test that the ingestion pipeline correctly formats raw yfinance data,
    flattens columns, handles dates, and stacks multiple tickers.
    """
    # 1. ARRANGE: Create a fake DataFrame that looks like Yahoo Finance output
    dates = pd.date_range(start="2024-01-01", periods=3)
    mock_df = pd.DataFrame({
        "Open": [100.0, 101.0, 102.0],
        "High": [105.0, 106.0, 107.0],
        "Low": [95.0, 96.0, 97.0],
        "Close": [102.0, 103.0, 104.0],
        "Volume": [1000, 1100, 1200]
    }, index=dates)
    mock_df.index.name = "Date"

    # Tell the mock to return this fake DataFrame whenever yf.download is called
    mock_download.return_value = mock_df

    # 2. ACT: Run our function with the mocked network
    tickers = ["SPY", "QQQ"]
    result = download_and_clean_data(tickers, "2024-01-01", "2024-01-03")

    # 3. ASSERT: Verify the logic did exactly what we expect
    assert len(result) == 6  # 3 days * 2 tickers = 6 rows
    assert "Date" in result.columns  # Date should be a column, not an index
    assert "Ticker" in result.columns
    assert set(result["Ticker"].unique()) == {"SPY", "QQQ"}

    # Verify yfinance was called exactly twice (once per ticker)
    assert mock_download.call_count == 2