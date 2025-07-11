import streamlit as st
import pandas as pd
import os
from datetime import date
import tempfile
import sys
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import uuid
import numpy as np

# Import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))

try:
    import stock_idss.src.data_fetcher as data_fetcher
    import stock_idss.src.features as features
    import stock_idss.src.predictor as predictor
    import stock_idss.src.fundamental_fetcher as fundamental_fetcher
    import stock_idss.src.enhanced_features as enhanced_features
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Stock IDSS Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .fundamental-section {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .prediction-badge {
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-weight: bold;
        text-align: center;
    }
    .buy { background-color: #d4edda; color: #155724; }
    .sell { background-color: #f8d7da; color: #721c24; }
    .hold { background-color: #fff3cd; color: #856404; }
</style>
""", unsafe_allow_html=True)

# Main title
st.title('Stock Intelligent Decision Support System')
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Ticker input
    ticker = st.text_input('Stock Ticker', 'AAPL').upper()
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Start Date', date(2022, 1, 1))
    with col2:
        end_date = st.date_input('End Date', date.today())
    
    # Feature options
    st.subheader("Features")
    use_fundamentals = st.checkbox("Include Fundamental Analysis", value=True, help="Add financial ratios and sector data")
    show_advanced_tech = st.checkbox("Advanced Technical Indicators", value=True, help="Include volatility and momentum indicators")
    
    # Model options
    st.subheader("Model Settings")
    prediction_threshold = st.slider("Buy/Sell Threshold (%)", -10.0, 10.0, 0.0, 0.5, 
                                   help="Minimum return threshold for Buy recommendation")
    
    # Run button
    st.markdown("---")
    run_button = st.button('Run Analysis', type='primary', use_container_width=True)

def format_currency(value):
    """Format large numbers as currency with appropriate suffixes."""
    if pd.isna(value) or value is None:
        return "N/A"
    
    if abs(value) >= 1e12:
        return f"${value/1e12:.1f}T"
    elif abs(value) >= 1e9:
        return f"${value/1e9:.1f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:.2f}"

def format_percentage(value):
    """Format value as percentage."""
    if pd.isna(value) or value is None:
        return "N/A"
    return f"{value:.2f}%"

def get_prediction_color(predicted_return, threshold):
    """Get color for prediction badge."""
    if predicted_return >= threshold:
        return "buy"
    elif predicted_return <= -threshold:
        return "sell"
    else:
        return "hold"

def get_prediction_text(predicted_return, threshold):
    """Get text for prediction badge."""
    if predicted_return >= threshold:
        return "BUY"
    elif predicted_return <= -threshold:
        return "SELL"
    else:
        return "HOLD"

def display_fundamental_summary(fundamental_data):
    """Display fundamental data in a clean summary."""
    if fundamental_data is None or fundamental_data.empty:
        return
    
    st.subheader("Fundamental Analysis")
    
    # Create columns for different categories
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Valuation Ratios**")
        if 'pe_ratio' in fundamental_data.columns:
            pe = fundamental_data['pe_ratio'].iloc[0]
            st.metric("P/E Ratio", f"{pe:.2f}" if not pd.isna(pe) else "N/A")
        
        if 'pb_ratio' in fundamental_data.columns:
            pb = fundamental_data['pb_ratio'].iloc[0]
            st.metric("P/B Ratio", f"{pb:.2f}" if not pd.isna(pb) else "N/A")
    
    with col2:
        st.markdown("**Financial Health**")
        if 'debt_to_equity' in fundamental_data.columns:
            de = fundamental_data['debt_to_equity'].iloc[0]
            st.metric("Debt/Equity", f"{de:.2f}" if not pd.isna(de) else "N/A")
        
        if 'current_ratio' in fundamental_data.columns:
            cr = fundamental_data['current_ratio'].iloc[0]
            st.metric("Current Ratio", f"{cr:.2f}" if not pd.isna(cr) else "N/A")
    
    with col3:
        st.markdown("**Growth & Returns**")
        if 'roe' in fundamental_data.columns:
            roe = fundamental_data['roe'].iloc[0]
            st.metric("ROE", format_percentage(roe * 100) if not pd.isna(roe) else "N/A")
        
        if 'revenue_growth_yoy' in fundamental_data.columns:
            growth = fundamental_data['revenue_growth_yoy'].iloc[0]
            st.metric("Revenue Growth", format_percentage(growth * 100) if not pd.isna(growth) else "N/A")
    
    # Company info
    if 'sector_classified' in fundamental_data.columns or 'market_cap_category' in fundamental_data.columns:
        st.markdown("**Company Information**")
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            if 'sector_classified' in fundamental_data.columns:
                sector = fundamental_data['sector_classified'].iloc[0]
                st.metric("Sector", sector if not pd.isna(sector) else "N/A")
        
        with info_col2:
            if 'market_cap_category' in fundamental_data.columns:
                mcap_cat = fundamental_data['market_cap_category'].iloc[0]
                st.metric("Market Cap", mcap_cat if not pd.isna(mcap_cat) else "N/A")
        
        with info_col3:
            if 'market_cap' in fundamental_data.columns:
                mcap = fundamental_data['market_cap'].iloc[0]
                st.metric("Market Cap Value", format_currency(mcap) if not pd.isna(mcap) else "N/A")

def display_technical_indicators(df):
    """Display technical indicators in a clean way."""
    st.subheader("Technical Indicators")
    
    # Check what columns are available
    available_columns = df.columns.tolist()
    st.info(f"Available columns: {', '.join(available_columns[:10])}{'...' if len(available_columns) > 10 else ''}")
    
    # Create subplot for technical indicators
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Price & Moving Averages', 'RSI', 'Volume'),
        vertical_spacing=0.08,
        row_heights=[0.5, 0.25, 0.25]
    )
    
    # Price and moving averages
    if 'Close' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['Close'], name='Close Price', line=dict(color='blue')),
            row=1, col=1
        )
    else:
        st.warning("Close price data not available for charting")
        return
    
    if 'SMA' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['SMA'], name='SMA', line=dict(color='orange')),
            row=1, col=1
        )
    
    if 'EMA' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['EMA'], name='EMA', line=dict(color='red')),
            row=1, col=1
        )
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['Date'], y=df['RSI'], name='RSI', line=dict(color='purple')),
            row=2, col=1
        )
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    else:
        st.warning("RSI data not available")
    
    # Volume
    if 'Volume' in df.columns:
        fig.add_trace(
            go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color='lightblue'),
            row=3, col=1
        )
    else:
        st.warning("Volume data not available")
    
    fig.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

def display_prediction_results(df_pred, threshold):
    """Display prediction results in a clean way."""
    st.subheader("Prediction Results")
    
    # Get latest prediction
    latest_pred = df_pred.iloc[-1]
    predicted_return = latest_pred.get('predicted_return', 0)
    
    # Create columns for key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        prediction_class = get_prediction_text(predicted_return, threshold)
        prediction_color = get_prediction_color(predicted_return, threshold)
        st.markdown(f"""
        <div class="prediction-badge {prediction_color}">
            {prediction_class}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Predicted Return", format_percentage(predicted_return * 100))
    
    with col3:
        if 'features_used' in df_pred.columns:
            features_used = latest_pred.get('features_used', 0)
            st.metric("Features Used", features_used)
    
    with col4:
        if 'Close' in df_pred.columns:
            current_price = latest_pred.get('Close', 0)
            st.metric("Current Price", format_currency(current_price))
    
    # Prediction chart
    fig = px.line(df_pred, x='Date', y='predicted_return', 
                  title='Predicted Return Over Time',
                  labels={'predicted_return': 'Predicted Return (%)'})
    fig.update_traces(line_color='blue')
    fig.add_hline(y=threshold, line_dash="dash", line_color="green", annotation_text="Buy Threshold")
    fig.add_hline(y=-threshold, line_dash="dash", line_color="red", annotation_text="Sell Threshold")
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

def run_enhanced_analysis():
    """Run the enhanced analysis with fundamental features."""
    with st.spinner('Running comprehensive analysis...'):
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # 1. Fetch price data
            st.info("Fetching price data...")
            raw_csv = data_fetcher.fetch_and_save_yfinance(ticker, str(start_date), str(end_date), save_dir=temp_dir)
            
            if not os.path.exists(raw_csv) or os.path.getsize(raw_csv) == 0:
                st.error('No price data fetched. Please check your ticker and date range.')
                return
            
            # 2. Fetch fundamental data (if requested)
            fundamental_data = None
            if use_fundamentals:
                st.info("Fetching fundamental data...")
                try:
                    fundamental_dir = os.path.join(temp_dir, 'fundamentals')
                    fundamental_fetcher.fetch_and_save_fundamentals(ticker, fundamental_dir)
                    
                    # Load fundamental ratios
                    ratios_file = os.path.join(fundamental_dir, f"{ticker}_ratios.csv")
                    if os.path.exists(ratios_file):
                        try:
                            fundamental_data = pd.read_csv(ratios_file)
                            if len(fundamental_data) > 0:
                                st.success(f"Fundamental data loaded: {len(fundamental_data.columns)} metrics")
                            else:
                                st.warning("Fundamental data file is empty")
                                fundamental_data = None
                        except Exception as e:
                            st.warning(f"Error reading fundamental data: {e}")
                            fundamental_data = None
                    else:
                        st.warning("Fundamental data file not found")
                except Exception as e:
                    st.warning(f"Fundamental data fetch failed: {e}")
                    fundamental_data = None
            
            # 3. Feature engineering
            st.info("Creating features...")
            processed_csv = os.path.join(temp_dir, f"{ticker}_processed.csv")
            
            if use_fundamentals and fundamental_data is not None:
                try:
                    enhanced_features.create_comprehensive_feature_set(
                        ticker=ticker,
                        price_csv=raw_csv,
                        fundamentals_dir=os.path.join(temp_dir, 'fundamentals'),
                        output_csv=processed_csv
                    )
                    st.success("Enhanced features created with fundamentals")
                except Exception as e:
                    st.warning(f"Enhanced features failed, falling back to basic: {e}")
                    features.process_and_save_with_indicators(raw_csv, processed_csv)
            else:
                features.process_and_save_with_indicators(raw_csv, processed_csv)
                st.success("Basic features created")
            
            # 4. Load model and predict
            st.info("Making predictions...")
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/model.pkl'))
            
            if not os.path.exists(model_path):
                st.error("Model not found. Please train a model first.")
                return
            
            model_data = predictor.load_model(model_path)
            df_pred = predictor.predict_returns(model_data, processed_csv)
            df_pred = predictor.apply_label(df_pred, threshold=prediction_threshold/100)
            
            st.success("Analysis complete!")
            
            # Store results in session state for persistence
            st.session_state['analysis_results'] = {
                'df_pred': df_pred,
                'fundamental_data': fundamental_data,
                'ticker': ticker,
                'threshold': prediction_threshold/100
            }
            
            # 5. Display results
            st.markdown("---")
            
            # Fundamental summary
            if fundamental_data is not None:
                display_fundamental_summary(fundamental_data)
                st.markdown("---")
            
            # Technical indicators
            st.info(f"Data shape: {df_pred.shape[0]} rows, {df_pred.shape[1]} columns")
            display_technical_indicators(df_pred)
            st.markdown("---")
            
            # Prediction results
            display_prediction_results(df_pred, prediction_threshold/100)
            
            # Store export data and success message in session state for consistent positioning
            st.session_state['export_data'] = {
                'predictions_csv': df_pred.to_csv(index=False).encode('utf-8'),
                'fundamental_csv': fundamental_data.to_csv(index=False).encode('utf-8') if fundamental_data is not None else None,
                'ticker': ticker
            }
            
        except Exception as e:
            st.error(f'Analysis failed: {e}')
            import traceback
            st.exception(traceback.format_exc())

def display_export_section():
    """Display export section in a consistent location with a fixed success message."""
    if 'export_data' in st.session_state:
        export_data = st.session_state['export_data']
        ticker = export_data['ticker']

        st.markdown("---")
        # Always show the success message at the top of the export section
        st.success(f"Analysis results available for {ticker}. Use the download buttons below to export data.")

        st.subheader("Export Results")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                'Download Predictions CSV',
                data=export_data['predictions_csv'],
                file_name=f'{ticker}_predictions.csv',
                mime='text/csv'
            )

        with col2:
            if export_data['fundamental_csv'] is not None:
                st.download_button(
                    'Download Fundamental Data',
                    data=export_data['fundamental_csv'],
                    file_name=f'{ticker}_fundamentals.csv',
                    mime='text/csv'
                )

        with col3:
            if st.button("Clear Results"):
                for key in ['analysis_results', 'export_data']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def display_stored_results():
    """Display results stored in session state."""
    if 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        df_pred = results['df_pred']
        fundamental_data = results['fundamental_data']
        ticker = results['ticker']
        threshold = results['threshold']
        
        # Fundamental summary
        if fundamental_data is not None:
            display_fundamental_summary(fundamental_data)
            st.markdown("---")
        
        # Technical indicators
        st.info(f"Data shape: {df_pred.shape[0]} rows, {df_pred.shape[1]} columns")
        display_technical_indicators(df_pred)
        st.markdown("---")
        
        # Prediction results
        display_prediction_results(df_pred, threshold)

# Main app logic
if run_button:
    if not ticker:
        st.error("Please enter a stock ticker.")
    elif start_date >= end_date:
        st.error("Start date must be before end date.")
    else:
        run_enhanced_analysis()
        # Analysis completed - success message will be shown in consistent location

# Display stored results if available (when not running new analysis)
elif 'analysis_results' in st.session_state:
    display_stored_results()

# Always display export section at the bottom if available
display_export_section()

# Instructions
if not run_button and 'analysis_results' not in st.session_state:
    st.info("""
    ### How to use this dashboard:
    
    1. **Enter a stock ticker** (e.g., AAPL, MSFT, GOOGL)
    2. **Select date range** for analysis
    3. **Choose features** to include in analysis
    4. **Click 'Run Analysis'** to get comprehensive predictions
    
    ### What you'll get:
    
    - **Fundamental Analysis**: P/E ratios, financial health, growth metrics
    - **Technical Indicators**: Price charts, RSI, volume analysis
    - **AI Predictions**: Buy/Sell/Hold recommendations with confidence
    - **Export Options**: Download results for further analysis
    """)

# Footer
st.markdown("---")
st.markdown("*Powered by Stock IDSS - Intelligent Decision Support System*") 