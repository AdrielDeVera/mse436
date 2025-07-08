# TODO.md

## 🔹 Data Ingestion
- [ ] Fetch data from `yfinance` and save to `data/raw/`
- [ ] Support optional `finnhub` via `.env`

## 🔹 Feature Engineering
- [ ] Load CSVs and compute indicators: SMA, RSI, EMA
- [ ] Create 6-month forward return (`target_return`)
- [ ] Drop NA rows and save to `data/processed/`

## 🔹 Model Training
- [ ] Train regression model with `XGBoost`
- [ ] Apply classification thresholds
- [ ] Save trained model to `models/model.pkl`

## 🔹 Prediction
- [ ] Load model and predict return + label
- [ ] Support batch inference for dashboard

## 🔹 Streamlit Dashboard
- [ ] Build UI for ticker selection and predictions
- [ ] Show:
  - Price chart with overlay
  - Prediction + label
  - Export CSV

## 🔹 Evaluation
- [ ] Backtest with actual vs predicted decisions
- [ ] Plot return curve, Sharpe, win/loss rate

## 🔹 Automation
- [ ] `run_pipeline.py` to connect all steps
- [ ] Add retraining logic (monthly)

## 🔹 API + Key Handling
- [ ] Load keys via `python-dotenv` in `env_loader.py`

## 🔹 Testing
- [ ] Add unit tests in `tests/` for:
  - Feature pipeline
  - Model interface
  - Predictor outputs
