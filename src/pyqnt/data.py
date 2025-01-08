import pytse_client as tse
import pandas as pd

def history(symbols: dict) -> pd.DataFrame:
    """
    Fetches and processes historical market data for the provided symbols from the Tehran Stock Exchange (TSE).

    This function downloads historical data for the given symbols, adjusts the prices to ensure continuity,
    and returns the data as a pandas DataFrame. The adjustment is necessary to account for corporate actions
    such as stock splits or dividends.

    Parameters:
    ----------
    symbols : dict
        A dictionary containing a list of stock symbols under the key 'tsetmc'. 
        Example:
        ```python
        symbols = {
            'tsetmc': ['وبصادر', 'فولاد', 'خودرو']
        }
        ```

    Returns:
    ----------
    pd.DataFrame
        A DataFrame containing the adjusted historical closing prices for the provided symbols.
        The DataFrame has the following structure:
        - Index: Date (datetime)
        - Columns: Symbol names (e.g., 'وبصادر', 'فولاد')
        - Values: Adjusted closing prices.

    Example:
    ----------
    ```python
    # Define the symbols to fetch
    symbols = {
        'tsetmc': ['وبصادر', 'فولاد', 'خودرو']
    }

    # Fetch historical data
    df = history(symbols)

    # Display the DataFrame
    print(df.head())
    ```

    Notes:
    ----------
    - The function uses the `tse.download` method to fetch data from the Tehran Stock Exchange.
    - Prices are adjusted to ensure continuity by accounting for corporate actions.
    - If no symbols are provided under the 'tsetmc' key, an empty DataFrame is returned.
    """
    df = pd.DataFrame()

    if symbols['tsetmc']:
        tickers = tse.download(symbols=symbols['tsetmc'], adjust=True)
        for ticker in tickers:
            # Adjusting the price to make the time series continuous
            temp = tickers[ticker][['date', 'close', 'adjClose', 'yesterday']].copy()
            temp.rename(columns={'close': ticker}, inplace=True)
            temp.set_index('date', inplace=True)
            temp['ratio'] = (temp['yesterday'].shift(-1) / temp['adjClose']).fillna(1.0)
            temp['ratio'] = temp.iloc[::-1]['ratio'].cumprod().iloc[::-1]
            temp[ticker] = temp[ticker].mul(temp['ratio'], axis=0)
            temp.drop(['ratio', 'adjClose', 'yesterday'], inplace=True, axis=1)
            df = pd.concat([df, temp], ignore_index=False)

    return df