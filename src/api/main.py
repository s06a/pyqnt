from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyqnt.quant import portfolio
from pyqnt.data import fetch_historical_data

app = FastAPI()

class PortfolioRequest(BaseModel):
    symbols: dict
    risk_free_rate: float = 0.2
    method: str = "gmv"
    budget: float = 0

@app.post("/portfolio")
def compute_portfolio(request: PortfolioRequest):
    try:
        # Fetch historical data
        data = fetch_historical_data(symbols=request.symbols)
        
        if data.empty:
            raise HTTPException(status_code=400, detail="No data returned for the provided symbols.")
        
        # Compute portfolio
        result = portfolio(
            data, 
            risk_free_rate=request.risk_free_rate, 
            method=request.method, 
            budget=request.budget
        )
        
        return {"portfolio": result.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))