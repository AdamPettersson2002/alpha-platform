import typer
from pathlib import Path
from alpha_platform.data.ingestion import run_ingestion

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

def main():
    app()

if __name__ == "__main__":
    main()