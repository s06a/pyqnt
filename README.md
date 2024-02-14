# Quant: A Portfolio Optimization Tool
Quant is a simple tool to create optimal portfolios based on historical data from different markets. For now, it supports two methods of portfolio optimization: Global Minimum Variance (GMV) and Maximum Sharpe Ratio (MSR).

# Features
- Retrieve data from various markets
- Optimize the portfolio weights based on GMV or MSR method
- Generate a report with the portfolio summary and performance metrics (not yet)

# Installation
'''bash
git clone https://github.com/s06a/quant.git
cd quant
pip3 install .
'''

# Examples
```python
import quant as qn

symbols = {
    "market": ["first_ticker", "second_ticker"],
}

df = qn.data.history(symbols)

portfolio = qn.quant.portfolio(df, risk_free_rate=0.2, method='gmv')

print(portfolio)
```

# Disclaimer
Quant is intended for educational purposes only. It does not provide any investment advice or guarantee any results. Do not use its output for real-life trading decisions.