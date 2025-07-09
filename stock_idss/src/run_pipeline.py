import os
import sys
from datetime import date
import tempfile
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../evaluation')))

import stock_idss.src.data_fetcher as data_fetcher
import stock_idss.src.features as features
import stock_idss.src.train_model as train_model
import stock_idss.src.predictor as predictor
import stock_idss.evaluation.backtest as backtest

def run_pipeline(ticker, start, end, model_path, results_dir, use_fundamentals=True):
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"=== Running pipeline for {ticker} from {start} to {end} ===")
    
    # 1. Fetch price data
    print("1. Fetching price data...")
    raw_csv = os.path.join(results_dir, f'{ticker}_raw.csv')
    data_fetcher.fetch_and_save_yfinance(ticker, start, end, save_dir=results_dir)
    
    # 2. Fetch fundamental data (if requested)
    if use_fundamentals:
        print("2. Fetching fundamental data...")
        try:
            import fundamental_fetcher
            fundamentals_dir = os.path.join(results_dir, 'fundamentals')
            fundamental_fetcher.fetch_and_save_fundamentals(ticker, fundamentals_dir)
        except ImportError:
            print("Warning: fundamental_fetcher not available, skipping fundamental data")
            use_fundamentals = False
    
    # 3. Feature engineering
    print("3. Feature engineering...")
    processed_csv = os.path.join(results_dir, f'{ticker}_processed.csv')
    
    if use_fundamentals:
        try:
            features.process_with_fundamentals(
                raw_csv, processed_csv, ticker, 
                fundamentals_dir=os.path.join(results_dir, 'fundamentals')
            )
        except Exception as e:
            print(f"Warning: Fundamental features failed, falling back to basic: {e}")
            features.process_and_save_with_indicators(raw_csv, processed_csv)
    else:
        features.process_and_save_with_indicators(raw_csv, processed_csv)
    
    # 4. Train model
    print("4. Training model...")
    train_model.train_xgboost_regressor(processed_csv, model_path)
    
    # 5. Predict
    print("5. Making predictions...")
    pred_csv = os.path.join(results_dir, f'{ticker}_pred.csv')
    model_data = predictor.load_model(model_path)
    df_pred = predictor.predict_returns(model_data, processed_csv)
    df_pred = predictor.apply_label(df_pred)
    df_pred.to_csv(pred_csv, index=False)
    
    # 6. Backtest
    print("6. Running backtest...")
    results = backtest.backtest_strategy(pred_csv)
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Win Rate: {results['win_rate']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe']:.2f}")
    
    return results

def run_monthly_retrain(ticker, start, end, model_path, results_dir):
    # Generate month start dates
    months = pd.date_range(start=start, end=end, freq='MS')
    for i in range(len(months)-1):
        m_start = months[i].strftime('%Y-%m-%d')
        m_end = (months[i+1] - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        print(f'\n=== Running pipeline for {m_start} to {m_end} ===')
        m_model_path = os.path.join(results_dir, f'model_{m_start}.pkl')
        m_results_dir = os.path.join(results_dir, f'{m_start}_results')
        run_pipeline(ticker, m_start, m_end, m_model_path, m_results_dir)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run full pipeline: fetch, features, train, predict, backtest.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol")
    parser.add_argument("--start", type=str, default="2022-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=str(date.today()), help="End date (YYYY-MM-DD)")
    parser.add_argument("--model_path", type=str, default="../models/model.pkl", help="Path to save model")
    parser.add_argument("--results_dir", type=str, default="../results/", help="Directory for outputs")
    parser.add_argument("--monthly_retrain", action="store_true", help="Run monthly retraining loop")
    parser.add_argument("--no-fundamentals", action="store_true", help="Skip fundamental features")
    args = parser.parse_args()
    
    use_fundamentals = not args.no_fundamentals
    
    if args.monthly_retrain:
        run_monthly_retrain(args.ticker, args.start, args.end, args.model_path, args.results_dir)
    else:
        run_pipeline(args.ticker, args.start, args.end, args.model_path, args.results_dir, use_fundamentals)
