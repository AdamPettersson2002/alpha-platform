import typer
from pathlib import Path
import pandas as pd
import numpy as np
from alpha_platform.data.ingestion import run_ingestion
from alpha_platform.features.builder import build_features
from alpha_platform.backtest.engine import run_iterative_backtest

app = typer.Typer(help="Alpha Platform CLI")

@app.command()
def hello():
    """Sanity command to verify the CLI is working."""
    print("alpha-platform is set up ✅")

@app.command()
def download(
    config: Path = typer.Option(
        ..., "--config", "-c", help="Path to the universe YAML config file"
    )
):
    """
    Download and cache daily OHLCV data based on a YAML configuration.
    """
    run_ingestion(config)


@app.command()
def features():
    """
    Load raw parquet data, build strictly-timed features, and save to a new parquet.
    """
    raw_path = Path("data/raw/universe_daily.parquet")
    out_path = Path("data/features/universe_features.parquet")

    if not raw_path.exists():
        print(f"Error: Raw data not found at {raw_path}. Run 'alpha download' first.")
        raise typer.Exit(1)

    print("Loading raw dataset...")
    df = pd.read_parquet(raw_path)

    print("Computing features and enforcing timing shifts...")
    features_df = build_features(df)

    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_parquet(out_path, index=False)

    print(f"✅ Features built and saved to {out_path}")
    print(f"Dataset shape: {features_df.shape}")


@app.command()
def backtest(
        costs: float = typer.Option(5.0, "--costs", help="Transaction costs in basis points (bps)"),
        capital: float = typer.Option(100000.0, "--capital", help="Starting capital")
):
    """
    Run a Wide-Matrix Iterative backtest using an Equal Weight baseline.
    """
    features_path = Path("data/features/universe_features.parquet")

    if not features_path.exists():
        print(f"Error: Features not found at {features_path}. Run 'alpha features' first.")
        raise typer.Exit(1)

    print(f"Loading features from {features_path}...")
    df = pd.read_parquet(features_path)

    print(f"Running Wide-Matrix Iterative backtest with {costs} bps costs...")
    results = run_iterative_backtest(df, initial_capital=capital, cost_bps=costs)

    # Compute high-level metrics for the terminal
    total_return = (results['cumulative_net'].iloc[-1] - 1) * 100

    # Only calculate vol and sharpe if we have returns
    if len(results) > 1 and results['net_ret'].std() > 0:
        annualized_vol = results['net_ret'].std() * np.sqrt(252) * 100
        sharpe = (results['net_ret'].mean() / results['net_ret'].std()) * np.sqrt(252)
    else:
        annualized_vol = 0.0
        sharpe = 0.0

    avg_daily_turnover = results['turnover'].mean() * 100

    print("\n[bold green]Backtest Complete ✅[/bold green]")
    print(f"Total Cumulative Return: {total_return:.2f}%")
    print(f"Annualized Volatility:   {annualized_vol:.2f}%")
    print(f"Annualized Sharpe Ratio: {sharpe:.2f}")
    print(f"Average Daily Turnover:  {avg_daily_turnover:.2f}%")

    # Save the results
    out_path = Path("data/reports/backtest_results.parquet")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_parquet(out_path)
    print(f"\nResults saved to {out_path}")


def main():
    app()

if __name__ == "__main__":
    main()