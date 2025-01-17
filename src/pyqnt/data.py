import pytse_client as tse
import pandas as pd
import ccxt.async_support as ccxt 
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector

class MarketDataFetcher:
    """
    A class to fetch and process historical OHLCV market data for TSE and cryptocurrency symbols asynchronously.
    Supports SOCKS5 proxy for cryptocurrency data fetching.
    """

    def __init__(self, exchange_id: str = 'binance', timeframe: str = '1d', proxy_url: str = None):
        """
        Initializes the MarketDataFetcher.

        Parameters:
        ----------
        exchange_id : str, optional
            The ID of the cryptocurrency exchange to use (default: 'binance').
        timeframe : str, optional
            The timeframe for cryptocurrency data (default: '1d' for daily).
        proxy_url : str, optional
            The SOCKS5 proxy URL (e.g., 'socks5://localhost:10808').
        """
        self.exchange_id = exchange_id
        self.timeframe = timeframe
        self.proxy_url = proxy_url

    def _adjust_tse_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adjusts OHLCV fields for TSE data.

        Parameters:
        ----------
        df : pd.DataFrame
            A DataFrame containing raw TSE OHLCV data.

        Returns:
        ----------
        pd.DataFrame
            A DataFrame with adjusted OHLCV data.
        """
        # Calculate adjustment ratio
        df['ratio'] = (df['yesterday'].shift(-1) / df['adjClose']).fillna(1.0)
        df['ratio'] = df.iloc[::-1]['ratio'].cumprod().iloc[::-1]

        # Adjust all OHLCV fields
        df['open'] = df['open'].mul(df['ratio'], axis=0)
        df['high'] = df['high'].mul(df['ratio'], axis=0)
        df['low'] = df['low'].mul(df['ratio'], axis=0)
        df['close'] = df['close'].mul(df['ratio'], axis=0)
        df['volume'] = df['volume'].div(df['ratio'], axis=0)  # Volume is inversely adjusted

        # Drop unnecessary columns
        df.drop(['ratio', 'adjClose', 'yesterday'], inplace=True, axis=1)

        return df

    async def fetch_tse_data(self, symbols: list) -> dict:
        """
        Fetches and adjusts OHLCV data for TSE symbols.

        Parameters:
        ----------
        symbols : list
            A list of TSE symbols.

        Returns:
        ----------
        dict
            A dictionary containing DataFrames with adjusted OHLCV data for each TSE symbol.
        """
        data = {}
        tickers = tse.download(symbols=symbols, adjust=True)

        for symbol in symbols:
            # Extract relevant columns
            temp = tickers[symbol][['date', 'open', 'high', 'low', 'close', 'volume', 'adjClose', 'yesterday']].copy()
            temp.set_index('date', inplace=True)

            # Adjust OHLCV fields
            temp = self._adjust_tse_prices(temp)

            # Store the adjusted data
            data[symbol] = temp

        return data

    async def fetch_crypto_data(self, symbols: list) -> dict:
        """
        Fetches OHLCV data for cryptocurrency symbols asynchronously using a SOCKS5 proxy.

        Parameters:
        ----------
        symbols : list
            A list of cryptocurrency symbols.

        Returns:
        ----------
        dict
            A dictionary containing DataFrames with OHLCV data for each cryptocurrency symbol.
        """
        data = {}

        # Set up SOCKS5 proxy if provided
        if self.proxy_url:
            connector = ProxyConnector.from_url(self.proxy_url)
        else:
            connector = None

        # Initialize the exchange with the proxy
        exchange_class = getattr(ccxt, self.exchange_id)
        async with aiohttp.ClientSession(connector=connector) as session:
            exchange = exchange_class({'session': session})

            for symbol in symbols:
                try:
                    all_ohlcv = []
                    since = 0

                    while True:
                        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe=self.timeframe, since=since, limit=1000)
                        if len(ohlcv) == 0:
                            break
                        all_ohlcv.extend(ohlcv)
                        since = ohlcv[-1][0] + 1

                    # Create DataFrame
                    temp = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    temp['date'] = pd.to_datetime(temp['timestamp'], unit='ms')
                    temp.set_index('date', inplace=True)
                    temp.drop(columns=['timestamp'], inplace=True)
                    data[symbol] = temp

                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")

            await exchange.close()  # Close the exchange session

        return data

    async def fetch_all_data(self, symbols: dict) -> dict:
        """
        Fetches OHLCV data for all provided symbols (TSE and cryptocurrency) asynchronously.

        Parameters:
        ----------
        symbols : dict
            A dictionary containing lists of symbols under the keys 'tse' and/or 'crypto'.

        Returns:
        ----------
        dict
            A dictionary containing DataFrames with OHLCV data for each symbol.
        """
        data = {}

        # Run TSE and crypto fetching concurrently
        tse_task = self.fetch_tse_data(symbols.get('tse', []))
        crypto_task = self.fetch_crypto_data(symbols.get('crypto', []))

        # Wait for both tasks to complete
        tse_data, crypto_data = await asyncio.gather(tse_task, crypto_task)

        # Combine the results
        data.update(tse_data)
        data.update(crypto_data)

        return data

async def main():
    # Example usage
    symbols = {
        "tse": ["وبصادر", "فولاد", "طلا"],  # Replace with your desired TSE symbols
        "crypto": ["BTC/USDT", "ETH/USDT"]  # Replace with your desired crypto symbols
    }

    # Initialize the fetcher with a SOCKS5 proxy
    fetcher = MarketDataFetcher(exchange_id='binance', timeframe='1d', proxy_url='socks5://localhost:10808')

    # Fetch all data asynchronously
    ohlcv_data = await fetcher.fetch_all_data(symbols)

    # Display the data
    for symbol, df in ohlcv_data.items():
        print(f"OHLCV data for {symbol}:")
        print(df.head())
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())