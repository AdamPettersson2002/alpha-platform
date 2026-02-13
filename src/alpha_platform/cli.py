import typer

app = typer.Typer(help="Alpha Platform CLI")

@app.command()
def hello():
    print("alpha-platform is set up ✅")

@app.command()
def backtest():
    print("Backtest engine coming soon...")

def main():
    app()

if __name__ == "__main__":
    main()