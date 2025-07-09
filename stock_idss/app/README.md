# Stock IDSS Dashboard

## Overview

The Stock IDSS Dashboard provides an intuitive interface for stock analysis and prediction using both technical and fundamental data.

## Available Dashboards

### 🚀 Enhanced Dashboard (Recommended)
**File:** `enhanced_dashboard.py`

**Features:**
- **Fundamental Analysis**: P/E ratios, financial health metrics, growth indicators
- **Advanced Technical Indicators**: Volatility, momentum, volume analysis
- **Sector Classification**: Industry and market cap categorization
- **Interactive Visualizations**: Multi-panel charts with thresholds
- **Export Capabilities**: Download predictions and fundamental data
- **Customizable Settings**: Adjustable thresholds and feature selection

### 📊 Basic Dashboard
**File:** `dashboard.py`

**Features:**
- Simple technical indicators (SMA, RSI, EMA)
- Basic predictions
- Quick analysis for simple use cases

## How to Run

### Option 1: Launcher (Recommended)
```bash
cd stock_idss/app
streamlit run launcher.py
```

### Option 2: Direct Launch
```bash
# Enhanced Dashboard
cd stock_idss/app
streamlit run enhanced_dashboard.py

# Basic Dashboard
cd stock_idss/app
streamlit run dashboard.py
```

## Dashboard Features

### 🏢 Fundamental Analysis
- **Valuation Ratios**: P/E, P/B, Debt-to-Equity, Current Ratio
- **Returns**: ROE, ROA
- **Growth**: Revenue Growth, Earnings Growth
- **Company Info**: Sector, Market Cap Category, Market Cap Value

### 📊 Technical Indicators
- **Price Charts**: Close price with SMA and EMA overlays
- **RSI**: Relative Strength Index with overbought/oversold levels
- **Volume**: Trading volume analysis
- **Advanced**: Volatility, momentum, Bollinger Bands (if available)

### 🎯 Predictions
- **Buy/Sell/Hold**: Color-coded recommendation badges
- **Predicted Return**: Percentage return forecast
- **Feature Count**: Number of features used in prediction
- **Threshold Lines**: Visual buy/sell thresholds on charts

### 📈 Visualizations
- **Multi-panel Charts**: Price, RSI, and volume in one view
- **Interactive Elements**: Hover tooltips, zoom, pan
- **Color Coding**: Green for buy, red for sell, yellow for hold
- **Professional Layout**: Clean, organized interface

## Configuration Options

### Sidebar Settings
- **Stock Ticker**: Enter any valid stock symbol
- **Date Range**: Select start and end dates for analysis
- **Feature Toggles**: Enable/disable fundamental and advanced technical features
- **Threshold Adjustment**: Customize buy/sell thresholds

### Export Options
- **Predictions CSV**: Download all prediction data
- **Fundamental Data**: Download financial ratios and metrics
- **Technical Data**: Download price and indicator data

## Example Usage

1. **Launch the dashboard**: `streamlit run enhanced_dashboard.py`
2. **Enter ticker**: Type "AAPL" for Apple
3. **Select dates**: Choose 2023-01-01 to 2024-01-01
4. **Enable features**: Check "Include Fundamental Analysis"
5. **Run analysis**: Click "Run Analysis"
6. **Review results**: Check fundamental metrics, technical charts, and predictions
7. **Export data**: Download results for further analysis

## Troubleshooting

### Common Issues

**"Model not found" error:**
- Train a model first using the pipeline: `python src/run_pipeline.py AAPL`

**"Fundamental data fetch failed":**
- Check internet connection
- Verify ticker symbol is valid
- Try a different date range

**Import errors:**
- Install required packages: `pip install -r requirements.txt`
- Check Python path configuration

### Performance Tips

- **Reduce date range** for faster analysis
- **Disable fundamental features** for basic analysis
- **Use basic dashboard** for simple technical analysis
- **Close other applications** to free up memory

## Data Sources

- **Price Data**: Yahoo Finance (yfinance)
- **Fundamental Data**: Yahoo Finance financial statements
- **Technical Indicators**: Calculated from price data
- **Sector Data**: Yahoo Finance company information

## Model Information

The dashboard uses trained XGBoost models that combine:
- Technical indicators (SMA, RSI, EMA, volatility, momentum)
- Fundamental ratios (P/E, P/B, ROE, ROA, etc.)
- Growth metrics (revenue growth, earnings growth)
- Market information (sector, market cap)

Models are automatically selected based on available features and provide feature importance rankings.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the main project documentation
3. Test with the provided test script: `python test_fundamental_features.py` 