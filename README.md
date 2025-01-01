# **Quant: A Portfolio Optimization Tool**  
Quant is a Python-based tool designed to construct optimal investment portfolios using historical market data. It currently supports two portfolio optimization techniques: **Global Minimum Variance (GMV)** and **Maximum Sharpe Ratio (MSR)**.


## **Features**  
- **Data Retrieval**: Fetch historical data from multiple markets.  
- **Portfolio Optimization**: Calculate optimal portfolio weights using GMV or MSR methods.  
- **Reporting**: (Upcoming) Generate a comprehensive portfolio summary and performance metrics.


## **Installation**  
To install Quant, clone the repository and install the package using `pip`:

```bash
git clone https://github.com/s06a/quant.git
cd quant
pip3 install .
```


## **Usage Examples**  
Below is an example of how to use Quant for portfolio optimization:  

```python
import quant as qn

# Define the symbols for data retrieval
symbols = {
    "tsetmc": ["وبصادر", "فولاد"],  # Example market symbols
}

# Retrieve historical market data
df = qn.data.history(symbols)

# Optimize portfolio weights using the GMV method
portfolio = qn.quant.portfolio(df, risk_free_rate=0.2, method='gmv')

# Print the optimized portfolio details
print(portfolio)
```


## **Disclaimer**  
Quant is developed for **educational purposes only** and does not provide investment advice or any form of financial guidance. The tool should not be used for real-world trading decisions, and its outputs are not guaranteed to yield specific results.
