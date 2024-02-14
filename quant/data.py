import pytse_client as tse
import pandas as pd

def history(symbols: dict) -> pd.DataFrame:
    """
    This function returns historical data of tickers as a dataframe.

    Parameters:
    ----------
        - symbols : dictionary
            provided symbols
    Returns:
    ----------
        - df : dataframe
            historical data of tickers
    """
    df = pd.DataFrame()

    if symbols['tsetmc']:
        tickers = tse.download(symbols=symbols['tsetmc'])
        for ticker in tickers:
            df.loc[:,ticker] = tickers[ticker]['close']

    return df