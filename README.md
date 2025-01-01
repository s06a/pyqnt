<h1 align="center">
    <a href="https://github.com/s06a/piquant"><img alt="PiQuant Logo" src="https://github.com/user-attachments/assets/5191a09c-4c00-40ab-92af-b5defa7835af" width="120"></a><br>PiQuant
</h1>

PiQuant is a Python-based tool for constructing optimal investment portfolios and performing quantitative financial analysis. The name combines the mathematical constant π (pi), symbolizing precision and elegance, with Python’s versatility and the power of structured analysis. PiQuant currently supports two portfolio optimization techniques: **Global Minimum Variance (GMV)** and **Maximum Sharpe Ratio (MSR)**.

## **Vision**

PiQuant aims to:
1. **Empower Financial Decisions**: Deliver tools for data-driven portfolio optimization.  
2. **Foster Exploration**: Expand into advanced quantitative techniques, risk management, and financial modeling.  

PiQuant embraces the uncertainty of markets, focusing on the journey of exploration and continuous learning.


## **Features**

- **Data Retrieval**: Access historical data from multiple markets.  
- **Portfolio Optimization**: Calculate optimal portfolio weights using GMV and MSR methods.  
- **Reporting (Upcoming)**: Generate detailed portfolio summaries and performance metrics.  


## **Installation**

To install PiQuant, clone the repository and install the package using `pip`:

```bash
git clone https://github.com/s06a/piquant.git
cd piquant
pip3 install .
```


## **Usage Examples**

```python
import piquant as pq

# Define the symbols for data retrieval
symbols = {
    "tsetmc": ["وبصادر", "فولاد"],  # Example market symbols
}

# Retrieve historical market data
df = pq.data.history(symbols)

# Optimize portfolio weights using the GMV method
portfolio = pq.quant.portfolio(df, risk_free_rate=0.2, method='gmv')

# Print the optimized portfolio details
print(portfolio)
```

## **Acknowledgments**

PiQuant is a work in progress—an experiment, a learning journey, and a tool to improve financial decision-making. The future is uncertain, but this project begins with curiosity, hope, and determination.

## **Disclaimer**

PiQuant is provided for scientific and educational purposes only. It is not intended as financial advice or a guarantee of financial outcomes. The author assumes no responsibility for any misuse, legal issues, or financial losses resulting from the use of this software.
