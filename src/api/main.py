from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyqnt.quant import portfolio
from pyqnt.data import MarketDataFetcher  # Import the new class
import uvicorn
import os
import asyncio
import pandas as pd

app = FastAPI()

class PortfolioRequest(BaseModel):
    symbols: dict
    risk_free_rate: float = 0.2
    method: str = "gmv"
    budget: float = 0

@app.post("/optimize-portfolio")
async def optimize_portfolio(request: PortfolioRequest):
    try:
        # Initialize the MarketDataFetcher
        fetcher = MarketDataFetcher(exchange_id='binance', timeframe='1d', proxy_url='socks5://localhost:10808')

        # Fetch historical data asynchronously
        data = await fetcher.fetch_all_data(request.symbols)
        
        if not data:
            raise HTTPException(status_code=400, detail="No data returned for the provided symbols.")
        
        # Extract close prices from the fetched data
        close_prices = pd.DataFrame({symbol: df['close'] for symbol, df in data.items()})

        # Compute portfolio using only close prices
        result = portfolio(
            close_prices, 
            risk_free_rate=request.risk_free_rate, 
            method=request.method, 
            budget=request.budget
        )
        
        return {"portfolio": result.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str = "127.0.0.1", port: int = 8000):
    """
    Run the FastAPI server.

    Parameters:
    ----------
    host : str, optional
        The host address to bind the server to (default: "127.0.0.1").
    port : int, optional
        The port to bind the server to (default: 8000).
    """
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # Read host and port from environment variables or use defaults
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    
    # Run the server
    run_server(host=host, port=port)