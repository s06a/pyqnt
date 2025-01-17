import click
import yaml
import requests
import asyncio
import pandas as pd
from pyqnt.data import MarketDataFetcher
from pyqnt.quant import portfolio

API_URL = "http://127.0.0.1:8000/optimize-portfolio"
HEALTH_CHECK_URL = "http://127.0.0.1:8000/health"  # Add a health check endpoint to your API

def is_api_up():
    """
    Check if the API is up by sending a health check request.

    Returns:
    ----------
    bool
        True if the API is up, False otherwise.
    """
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

async def fetch_data(symbols):
    """
    Fetch OHLCV data for the provided symbols using MarketDataFetcher.

    Parameters:
    ----------
    symbols : dict
        A dictionary containing lists of symbols under the keys 'tse' and/or 'crypto'.

    Returns:
    ----------
    dict
        A dictionary containing DataFrames with OHLCV data for each symbol.
    """
    fetcher = MarketDataFetcher(exchange_id='binance', timeframe='1d', proxy_url='socks5://localhost:10808')
    return await fetcher.fetch_all_data(symbols)

def optimize_portfolio_locally(symbols, risk_free_rate, method, budget):
    """
    Optimize the portfolio locally without using the API.
    Uses only close prices for optimization, matching the API logic.

    Parameters:
    ----------
    symbols : dict
        A dictionary containing lists of symbols under the keys 'tse' and/or 'crypto'.
    risk_free_rate : float
        The annual risk-free rate.
    method : str
        The optimization method: 'gmv' (Global Minimum Variance) or 'msr' (Maximum Sharpe Ratio).
    budget : float
        The total budget allocation for the portfolio.

    Returns:
    ----------
    dict
        A dictionary containing the optimized portfolio weights.
    """
    # Fetch data asynchronously
    data = asyncio.run(fetch_data(symbols))

    # Extract close prices from the fetched data
    close_prices = pd.DataFrame({symbol: df['close'] for symbol, df in data.items()})

    # Compute portfolio using only close prices
    result = portfolio(
        close_prices, 
        risk_free_rate=risk_free_rate, 
        method=method, 
        budget=budget
    )

    # Convert the result to a dictionary
    return {"portfolio": result.to_dict(orient="records")}

@click.group()
def pyqnt():
    """pyqnt CLI for portfolio optimization."""
    pass

@pyqnt.command()
@click.option('--file', type=click.Path(exists=True), required=True, help="Path to the YAML file containing stock symbols.")
@click.option('--method', type=click.Choice(['gmv', 'msr']), default='gmv', help="Optimization method: 'gmv' (Global Minimum Variance) or 'msr' (Maximum Sharpe Ratio)")
@click.option('--risk-free-rate', default=0.2, help="Annual risk-free rate (default: 0.2)")
@click.option('--budget', default=0, help="Total budget allocation for the portfolio (default: 0, meaning percentage-based weights only)")
def optimize(file, method, risk_free_rate, budget):
    """
    Optimize a portfolio using the specified method and input symbols from a YAML file.
    If the API is up, it will use the API; otherwise, it will compute the portfolio locally.
    Only close prices are used for optimization.
    """
    # Load symbols from YAML file
    try:
        with open(file, 'r', encoding='utf-8') as f:
            symbols_data = yaml.safe_load(f)

        # Validate the YAML structure
        if not symbols_data or not isinstance(symbols_data, dict):
            click.echo("Error: Invalid YAML format. Expected a dictionary with 'tse' and/or 'crypto' keys.", err=True)
            return

        # Ensure at least one of 'tse' or 'crypto' is present
        if "tse" not in symbols_data and "crypto" not in symbols_data:
            click.echo("Error: YAML file must contain at least one of 'tse' or 'crypto' keys.", err=True)
            return

        # Validate that 'tse' and 'crypto' are lists (if they exist)
        if "tse" in symbols_data and not isinstance(symbols_data["tse"], list):
            click.echo("Error: 'tse' must be a list of symbols.", err=True)
            return
        if "crypto" in symbols_data and not isinstance(symbols_data["crypto"], list):
            click.echo("Error: 'crypto' must be a list of symbols.", err=True)
            return

    except Exception as e:
        click.echo(f"Error reading YAML file: {e}", err=True)
        return

    # Prepare payload
    payload = {
        "symbols": symbols_data,
        "risk_free_rate": risk_free_rate,
        "method": method,
        "budget": budget
    }

    # Check if the API is up
    if is_api_up():
        click.echo("API is up. Using API for portfolio optimization...")
        try:
            # Send request to the API
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            data = response.json()
        except requests.exceptions.RequestException as e:
            click.echo(f"Error: Unable to connect to API. Falling back to local computation. {e}", err=True)
            data = optimize_portfolio_locally(**payload)
    else:
        click.echo("API is down. Falling back to local computation...")
        data = optimize_portfolio_locally(**payload)

    # Display results
    click.echo("\nOptimized Portfolio Weights:")
    for item in data.get("portfolio", []):
        click.echo(f"Ticker: {item['ticker']}, Weight: {item['weight']:.2f}")
        if "amount" in item:
            click.echo(f"  Amount: {item['amount']:.2f}")

if __name__ == "__main__":
    pyqnt()