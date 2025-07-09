#!/usr/bin/env python3
"""
Dashboard Launcher for Stock IDSS
Choose between basic and enhanced dashboards
"""

import streamlit as st
import subprocess
import sys
import os

def main():
    st.set_page_config(
        page_title="Stock IDSS - Dashboard Launcher",
        page_icon="🚀",
        layout="centered"
    )
    
    st.title("🚀 Stock IDSS Dashboard Launcher")
    st.markdown("---")
    
    st.markdown("""
    Welcome to the Stock Intelligent Decision Support System!
    
    Choose your dashboard experience:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Basic Dashboard
        - Simple technical indicators
        - Basic predictions
        - Quick analysis
        """)
        
        if st.button("Launch Basic Dashboard", type="secondary", use_container_width=True):
            # Launch basic dashboard
            subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    
    with col2:
        st.markdown("""
        ### 🚀 Enhanced Dashboard
        - **Fundamental analysis** (P/E, P/B, ROE, etc.)
        - **Advanced technical indicators**
        - **Sector classification**
        - **Market cap analysis**
        - **Improved visualizations**
        - **Export capabilities**
        """)
        
        if st.button("Launch Enhanced Dashboard", type="primary", use_container_width=True):
            # Launch enhanced dashboard
            subprocess.run([sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py"])
    
    st.markdown("---")
    
    st.markdown("""
    ### 📋 What's New in Enhanced Dashboard:
    
    **🏢 Fundamental Analysis:**
    - P/E Ratio, P/B Ratio, Debt-to-Equity
    - Current Ratio, ROE, ROA
    - Revenue Growth, Earnings Growth
    - Sector Classification, Market Cap Categories
    
    **📊 Advanced Technical Features:**
    - Volatility measures (20-day, 60-day)
    - Momentum indicators (5-day, 20-day, 60-day)
    - Volume analysis and ratios
    - Price vs Moving Average comparisons
    - Bollinger Bands (if available)
    
    **🎯 Enhanced Predictions:**
    - More accurate models with 25+ features
    - Feature importance rankings
    - Confidence indicators
    - Customizable thresholds
    
    **📈 Better Visualizations:**
    - Multi-panel technical charts
    - Color-coded prediction badges
    - Interactive charts with thresholds
    - Clean, professional layout
    """)
    
    st.markdown("---")
    
    # System requirements
    with st.expander("🔧 System Requirements"):
        st.markdown("""
        **Required Packages:**
        - streamlit
        - pandas
        - yfinance
        - plotly
        - numpy
        - xgboost
        - scikit-learn
        
        **Optional (for enhanced features):**
        - pandas_ta (for advanced technical indicators)
        
        **Install with:**
        ```bash
        pip install -r requirements.txt
        ```
        """)
    
    # Quick start guide
    with st.expander("📖 Quick Start Guide"):
        st.markdown("""
        1. **Choose a dashboard** (Enhanced recommended)
        2. **Enter a stock ticker** (e.g., AAPL, MSFT, GOOGL)
        3. **Select date range** for analysis
        4. **Configure features** (fundamental analysis, etc.)
        5. **Click 'Run Analysis'** to get predictions
        6. **Review results** and download data
        
        **Example tickers to try:**
        - AAPL (Apple)
        - MSFT (Microsoft)
        - GOOGL (Alphabet)
        - TSLA (Tesla)
        - NVDA (NVIDIA)
        """)

if __name__ == "__main__":
    main() 