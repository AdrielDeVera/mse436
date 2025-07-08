import streamlit as st
import pandas as pd
import os
from datetime import date
import tempfile
import sys
import plotly.express as px
import uuid

# Import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
import stock_idss.src.data_fetcher as data_fetcher
import stock_idss.src.features as features
import stock_idss.src.predictor as predictor   

st.title('Stock Return Prediction Dashboard')
st.info(f"Python executable: {sys.executable}")

# Sidebar for ticker and date selection
ticker = st.sidebar.text_input('Ticker', 'AAPL')
start_date = st.sidebar.date_input('Start Date', date(2022, 1, 1))
end_date = st.sidebar.date_input('End Date', date.today())

def run_prediction():
    with st.spinner('Fetching data and running prediction...'):
        try:
            # Use the file path returned by fetch_and_save_yfinance
            try:
                raw_csv = data_fetcher.fetch_and_save_yfinance(ticker, str(start_date), str(end_date), save_dir=tempfile.gettempdir())
                if not os.path.exists(raw_csv) or os.path.getsize(raw_csv) == 0:
                    st.error('No data was fetched from yfinance. Please check your ticker and date range.')
                    return
                df_raw = pd.read_csv(raw_csv)
                st.info(f"Fetched {df_raw.shape[0]} rows, {df_raw.shape[1]} columns from yfinance.")
                if df_raw.empty:
                    st.error('Fetched data is empty. Please check your ticker and date range.')
                    return
            except Exception as e:
                st.error(f'Error fetching data from yfinance: {e}')
                return

            processed_csv = os.path.join(tempfile.gettempdir(), f"processed_{uuid.uuid4().hex}.csv")
            try:
                # Use smaller window sizes for indicators and target return
                features.process_and_save_with_indicators(
                    raw_csv, processed_csv, sma_window=7, rsi_window=7, ema_window=7, forward_days=14
                )
                if not os.path.exists(processed_csv) or os.path.getsize(processed_csv) == 0:
                    st.error('Feature processing produced an empty file. Check your input data and feature code.')
                    return
                df_check = pd.read_csv(processed_csv)
                st.info(f"Processed data: {df_check.shape[0]} rows, {df_check.shape[1]} columns.")
                if df_check.empty or df_check.shape[1] == 0:
                    st.error('No data found in the processed CSV after feature engineering. Please check your ticker and date range.')
                    return
            except Exception as e:
                st.error(f'Error during feature processing: {e}')
                return

            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/model.pkl'))
            try:
                predictor.model = predictor.load_model(model_path)
                df_pred = predictor.predict_returns(predictor.model, processed_csv)
                df_pred = predictor.apply_label(df_pred)
            except Exception as e:
                st.error(f'Error during prediction/model step: {e}')
                return

            st.success('Prediction complete!')
            # Show table
            st.dataframe(df_pred[['Date', 'Close', 'predicted_return', 'predicted_label']])
            # Show price chart with overlay
            fig = px.scatter(df_pred, x='Date', y='Close', color='predicted_label',
                             color_discrete_map={0: 'red', 1: 'green'},
                             title='Price Chart with Prediction Overlay')
            fig.add_scatter(x=df_pred['Date'], y=df_pred['Close'], mode='lines', name='Close')
            st.plotly_chart(fig, use_container_width=True)
            # Show prediction + label summary
            st.markdown('### Prediction Summary')
            st.write(df_pred[['predicted_return', 'predicted_label']].describe())
            # Export CSV
            csv_bytes = df_pred.to_csv(index=False).encode('utf-8')
            st.download_button('Export Predictions as CSV', data=csv_bytes, file_name=f'{ticker}_predictions.csv', mime='text/csv')
        except Exception as e:
            st.error(f'Error: {e}')

if st.sidebar.button('Fetch & Predict'):
    run_prediction()
