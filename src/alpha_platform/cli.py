import typer
from pathlib import Path
from alpha_platform.data.ingestion import run_ingestion
import pandas as pd
from alpha_platform.features.builder import build_features


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


def main():
    app()

if __name__ == "__main__":
    main()