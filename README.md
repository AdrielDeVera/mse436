# 📈 Intelligent Stock Decision Support System (IDSS)

This project is a Machine Learning-powered **Stock Picking Decision Support System** designed to help everyday investors and financial advisors make better data-driven investment decisions. It provides 6–12 month **return predictions** and **Buy/Hold/Sell** recommendations through a user-friendly dashboard.

## 🚀 Demo

[Watch the Demo](https://drive.google.com/file/d/1gVDYxHUWem88raPcUi8XKaMGUd-2Eo8t/view)

---

## 🧠 Problem Statement

Investors face:
- **Information overload** from thousands of stocks and metrics.
- **Market complexity** and emotional decision-making.
- A need for **objective, repeatable insights** over gut instinct.

This system simplifies stock analysis using predictive models and clean visualizations, turning raw data into actionable guidance.

---

## ⚙️ Features

- 📊 **Return Forecasts** (Regression)
- 🟢🔴 **Buy/Sell Labels** (Classification)
- 📈 Interactive visualizations: price trends, RSI, sector breakdowns
- 🔧 User controls: Ticker search, thresholds, date ranges
- 📤 Export results to CSV

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python (pandas, scikit-learn, XGBoost)
- **Data Sources**: Yahoo Finance, Finnhub
- **Storage**: Local CSVs (future: PostgreSQL/cloud bucket)
- **Modeling**: Pickled ML models (regression + classification)
- **Infrastructure**: CI-ready for cloud deployment (Heroku/AWS)

---

## 🔍 How It Works

- Ingests historical stock data using `yfinance` and `finnhub`
- Preprocesses financial ratios and derived indicators (P/E, YoY Growth)
- Trains ML models to predict returns and generate stock recommendations
- Displays results in an intuitive dashboard with charts and toggles

---

## 📦 Requirements

- Python 3.11+
- `streamlit`, `pandas`, `scikit-learn`, `xgboost`, `yfinance`, `finnhub-python`, `plotly`, `python-dotenv`

Install with:
```bash
pip install -r requirements.txt



