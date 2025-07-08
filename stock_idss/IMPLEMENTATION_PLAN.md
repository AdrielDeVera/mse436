# IMPLEMENTATION_PLAN.md

## 🧱 High-Level Plan

We will implement a modular stock forecasting pipeline that:
- Ingests data from public APIs
- Computes financial indicators
- Trains a regression model to predict 6-month return
- Classifies into Buy/Hold/Sell decisions
- Displays results in a Streamlit dashboard

---

## 📁 Modules & Responsibilities

### 1. `data_fetcher.py`
- Uses `yfinance` by default
- Fetches OHLCV data
- Saves data as `data/raw/{TICKER}.csv`

### 2. `features.py`
- Loads raw data
- Computes indicators (SMA, RSI, volatility, etc.)
- Adds 6-month forward return as `target_return`
- Saves processed data to `data/processed/`

### 3. `train_model.py`
- Trains regression model (XGBoost)
- Performs time-based cross-validation
- Converts predictions into Buy/Hold/Sell
- Saves model to `models/`

### 4. `predictor.py`
- Loads saved model
- Returns predictions for new data

### 5. `run_pipeline.py`
- Runs: fetch → feature → train → predict
- Saves outputs
- Can be scheduled monthly

### 6. `dashboard.py`
- Streamlit UI
- Select tickers, show predictions + label
- Display feature explanation and export

### 7. `backtest.py`
- Runs backtest on past labels
- Calculates returns, Sharpe ratio, drawdown

---

## 🧩 Dependencies
- `pandas`, `yfinance`, `scikit-learn`, `xgboost`, `streamlit`, `shap`, `joblib`

---

## 🔒 Security
- API keys via `.env` file (`utils/env_loader.py`)

---

## 🧪 Testing Plan
- Basic unit tests for feature generation and modeling
- Integration test in `run_pipeline.py`
