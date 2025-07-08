import os
import pandas as pd

try:
    import pandas_ta as ta
except ImportError:
    ta = None

def load_stock_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, header=0, parse_dates=['Date'])
    if 'Close' not in df.columns:
        df = pd.read_csv(file_path, header=2, parse_dates=['Date'])
    # Now 'Date' is always present and parsed as datetime
    for col in df.columns:
        if col != 'Date':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def add_indicators(df: pd.DataFrame, sma_window=14, rsi_window=14, ema_window=14) -> pd.DataFrame:
    if ta is None:
        raise ImportError("pandas_ta is required for indicator computation. Install with 'pip install pandas_ta'.")
    df = df.copy()
    df['SMA'] = ta.sma(df['Close'], length=sma_window)
    df['RSI'] = ta.rsi(df['Close'], length=rsi_window)
    df['EMA'] = ta.ema(df['Close'], length=ema_window)
    return df

def add_target_return(df: pd.DataFrame, forward_days=126) -> pd.DataFrame:
    df = df.copy()
    df['target_return'] = df['Close'].shift(-forward_days) / df['Close'] - 1
    return df

def process_and_save_with_indicators(input_csv: str, output_csv: str, sma_window=14, rsi_window=14, ema_window=14, forward_days=126, drop_na=True):
    df = load_stock_csv(input_csv)
    df = add_indicators(df, sma_window, rsi_window, ema_window)
    df = add_target_return(df, forward_days)
    if drop_na:
        # Only drop rows where features or target are NaN
        df = df.dropna(subset=['SMA', 'RSI', 'EMA', 'target_return'])
    # Ensure Date column is present before saving
    if 'Date' not in df.columns and isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index().rename(columns={'index': 'Date'})
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compute indicators and save processed CSV.")
    parser.add_argument("input_csv", type=str, help="Input CSV file path")
    parser.add_argument("output_csv", type=str, help="Output CSV file path")
    parser.add_argument("--sma_window", type=int, default=14)
    parser.add_argument("--rsi_window", type=int, default=14)
    parser.add_argument("--ema_window", type=int, default=14)
    parser.add_argument("--forward_days", type=int, default=126, help="Forward window for target_return")
    parser.add_argument("--drop_na", action="store_true", help="Drop NA rows before saving (default: True)")
    parser.add_argument("--no-drop_na", dest="drop_na", action="store_false", help="Do not drop NA rows")
    parser.set_defaults(drop_na=True)
    args = parser.parse_args()
    process_and_save_with_indicators(args.input_csv, args.output_csv, args.sma_window, args.rsi_window, args.ema_window, args.forward_days, args.drop_na)
