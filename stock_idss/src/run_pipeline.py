import os
import sys
from datetime import date
import tempfile
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../evaluation')))

import data_fetcher
import features
import train_model
import predictor
import evaluation.backtest as backtest

def run_pipeline(ticker, start, end, model_path, results_dir):
    os.makedirs(results_dir, exist_ok=True)
    # 1. Fetch data
    raw_csv = os.path.join(results_dir, f'{ticker}_raw.csv')
    data_fetcher.fetch_and_save_yfinance(ticker, start, end, save_dir=results_dir)
    # 2. Feature engineering
    processed_csv = os.path.join(results_dir, f'{ticker}_processed.csv')
    features.process_and_save_with_indicators(raw_csv, processed_csv)
    # 3. Train model
    train_model.train_xgboost_regressor(processed_csv, model_path)
    # 4. Predict
    pred_csv = os.path.join(results_dir, f'{ticker}_pred.csv')
    model = predictor.load_model(model_path)
    df_pred = predictor.predict_returns(model, processed_csv)
    df_pred = predictor.apply_label(df_pred)
    df_pred.to_csv(pred_csv, index=False)
    # 5. Backtest
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
    args = parser.parse_args()
    if args.monthly_retrain:
        run_monthly_retrain(args.ticker, args.start, args.end, args.model_path, args.results_dir)
    else:
        run_pipeline(args.ticker, args.start, args.end, args.model_path, args.results_dir)
