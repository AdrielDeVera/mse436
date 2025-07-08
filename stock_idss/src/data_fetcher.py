import os
import sys
from typing import Optional
import yfinance as yf
import requests
import pandas as pd

# Try to import get_env_variable, fallback to sys.path hack if needed
try:
    from stock_idss.utils.env_loader import get_env_variable
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
    from utils.env_loader import get_env_variable

def fetch_and_save_yfinance(ticker: str, start: str, end: str, save_dir: str = '../data/raw/') -> str:
    """
    Fetch historical stock data from yfinance and save as CSV.
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        start (str): Start date in 'YYYY-MM-DD'.
        end (str): End date in 'YYYY-MM-DD'.
        save_dir (str): Directory to save the CSV file.
    Returns:
        str: Path to the saved CSV file.
    """
    os.makedirs(save_dir, exist_ok=True)
    df = yf.download(ticker, start=start, end=end)
    if df is None or df.empty:
        raise ValueError(f"No data fetched for {ticker} from {start} to {end}.")
    df.index.name = 'Date'  # Name the index for clarity
    df = df.reset_index()   # Move index to a column
    file_path = os.path.join(save_dir, f"{ticker}_{start}_{end}.csv")
    df.to_csv(file_path, index=False)  # Save with Date as a column
    return file_path

def fetch_and_save_finnhub(ticker: str, start: str, end: str, save_dir: str = '../data/raw/') -> str:
    """
    Fetch historical stock data from finnhub and save as CSV.
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL').
        start (str): Start date in 'YYYY-MM-DD'.
        end (str): End date in 'YYYY-MM-DD'.
        save_dir (str): Directory to save the CSV file.
    Returns:
        str: Path to the saved CSV file.
    """
    os.makedirs(save_dir, exist_ok=True)
    api_key = get_env_variable('FINNHUB_API_KEY')
    url = f'https://finnhub.io/api/v1/stock/candle'
    params = {
        'symbol': ticker,
        'resolution': 'D',
        'from': int(pd.to_datetime(start).value // 10**9),
        'to': int(pd.to_datetime(end).value // 10**9),
        'token': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('s') != 'ok':
        raise ValueError(f"No data fetched for {ticker} from {start} to {end} via finnhub: {data}")
    df = pd.DataFrame({
        'Date': pd.to_datetime(data['t'], unit='s'),
        'Open': data['o'],
        'High': data['h'],
        'Low': data['l'],
        'Close': data['c'],
        'Volume': data['v']
    })
    file_path = os.path.join(save_dir, f"{ticker}_{start}_{end}_finnhub.csv")
    df.to_csv(file_path, index=False)
    return file_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch stock data from yfinance and save as CSV.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., 'AAPL')")
    parser.add_argument("--start", type=str, required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--save_dir", type=str, default="../data/raw/", help="Directory to save CSV")
    args = parser.parse_args()
    path = fetch_and_save_yfinance(args.ticker, args.start, args.end, args.save_dir)
    print(f"Saved data to {path}")
