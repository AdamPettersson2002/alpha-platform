import yaml
from pathlib import Path
import pandas as pd
import yfinance as yf
from rich.console import Console
console = Console()


def load_config(config_path: str | Path) -> dict:
    """
    Loads a YAML configuration file and returns it as a dictionary.

    Args:
        config_path: The path to the YAML file.

    Returns:
        A dictionary containing the configuration parameters.
    """
    path_obj = Path(config_path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path_obj}")

    with open(path_obj, "r") as file:
        config = yaml.safe_load(file)

    return config


def download_and_clean_data(tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Downloads OHLCV data, cleans it, and returns a long-format DataFrame.
    """
    dfs = []
    for ticker in tickers:
        console.print(f"Downloading [cyan]{ticker}[/cyan]...")

        # Download data from Yahoo Finance
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if df.empty:
            console.print(f"[yellow]Warning: No data found for {ticker}[/yellow]")
            continue

        # 1. Flatten MultiIndex columns (Grabs 'Close', 'Open', etc., drops 'SPY')
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 2. Move Date from the index to a column
        df = df.reset_index()

        # 3. Standardize the 'Date' column name just in case yfinance lowercased it
        df.rename(columns={'index': 'Date', 'date': 'Date'}, inplace=True)

        # 4. Strip timezones so all assets share the exact same calendar
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        df['Ticker'] = ticker

        # 5. Sort chronologically
        df = df.sort_values('Date')

        # 6. DEFENSIVE PROGRAMMING: Only forward-fill columns that actually exist!
        possible_price_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        cols_to_ffill = [col for col in possible_price_cols if col in df.columns]

        # Forward fill up to 5 days of missing prices to prevent data leakage.
        if cols_to_ffill:
            df[cols_to_ffill] = df[cols_to_ffill].ffill(limit=5)

        dfs.append(df)

    if not dfs:
        raise ValueError("No data downloaded. Check your internet or universe.yaml.")

    # Stack all tickers into one long-format table
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df


def print_summary(df: pd.DataFrame):
    """Prints a high-level summary of the dataset."""
    n_assets = df['Ticker'].nunique()
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    total_rows = len(df)
    missing_data = df.isnull().sum().to_dict()

    console.print("\n[bold green]Data Ingestion Summary ✅[/bold green]")
    console.print(f"Assets ({n_assets}): {list(df['Ticker'].unique())}")
    console.print(f"Date Range: {min_date} to {max_date}")
    console.print(f"Total Rows: {total_rows}")
    console.print(f"Missing Values: {missing_data}")


def run_ingestion(config_path: Path):
    """Orchestrates the loading, downloading, summarizing, and saving."""
    config = load_config(config_path)
    tickers = config.get("tickers", [])
    start_date = config.get("start_date")
    end_date = config.get("end_date")
    output_dir = Path(config.get("output_dir", "data/raw"))

    # Ensure the data/raw folder exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run the pipeline
    df = download_and_clean_data(tickers, start_date, end_date)
    print_summary(df)

    # Save to Parquet
    out_file = output_dir / "universe_daily.parquet"
    df.to_parquet(out_file, index=False)
    console.print(f"[bold blue]Data successfully saved to {out_file}[/bold blue]\n")