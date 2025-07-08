# PLANNED_INTERFACE.md

## 🧠 Project Purpose
Create an Intelligent Decision Support System (IDSS) for everyday investors to:
- Predict 6–12 month stock returns (regression)
- Classify each stock as Buy, Hold, or Sell (classification)
- Provide insights through a simple dashboard (Streamlit)

---

## 👤 End Users
- Retail investors
- Finance students
- Analysts needing quick Buy/Hold/Sell signals

---

## 📥 Inputs
- Stock tickers (default: AAPL, MSFT, AMZN, GOOG, META, NVDA, TSLA, JPM, BRK.B, UNH)
- Optional: date range selector
- Optional: upload custom CSV file with price history

---

## 📤 Outputs
- Predicted 6-month return per stock
- Buy / Hold / Sell label
- Feature contribution explanation (optional: SHAP or GPT)
- Visual charts of price & prediction
- Downloadable CSV of signals

---

## 🖥 Interface Components (Streamlit)
- Sidebar:
  - Ticker selector
  - Date range input
  - Upload CSV (optional)
- Main view:
  - Price chart with moving averages
  - Predicted return and label
  - Explanation section
  - Download/export results

---

## 🧑‍💻 Developer Interface (Backend Modules)
- `data_fetcher.py`: Pulls stock data (yfinance/Finnhub)
- `features.py`: Generates indicators and labels
- `train_model.py`: Trains regression + classification model
- `predictor.py`: Loads model and runs inference
- `run_pipeline.py`: Ties full flow together
- `dashboard.py`: Streamlit UI
- `backtest.py`: Validates strategy
