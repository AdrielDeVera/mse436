import streamlit as st
import pandas as pd
import os
from datetime import date
import tempfile
import sys
import plotly.express as px

# Import project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))
import src.data_fetcher as data_fetcher
import src.features as features
import src.predictor as predictor   

st.title('Stock Return Prediction Dashboard')

# Sidebar for ticker and date selection
ticker = st.sidebar.text_input('Ticker', 'AAPL')
start_date = st.sidebar.date_input('Start Date', date(2022, 1, 1))
end_date = st.sidebar.date_input('End Date', date.today())

def run_prediction():
    with st.spinner('Fetching data and running prediction...'):
        try:
            raw_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
            data_fetcher.fetch_and_save_yfinance(ticker, str(start_date), str(end_date), save_dir=os.path.dirname(raw_csv))
            processed_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
            features.process_and_save_with_indicators(raw_csv, processed_csv)
            # Check if processed CSV has data
            try:
                df_check = pd.read_csv(processed_csv)
                if df_check.empty or df_check.shape[1] == 0:
                    st.error('No data found in the processed CSV. Please check your ticker and date range.')
                    return
            except Exception as e:
                st.error(f'Error reading processed CSV: {e}')
                return
            model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/model.pkl'))
            pred_csv = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
            predictor.model = predictor.load_model(model_path)
            df_pred = predictor.predict_returns(predictor.model, processed_csv)
            df_pred = predictor.apply_label(df_pred)
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
