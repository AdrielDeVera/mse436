import os
import sys
import pytest
from unittest import mock
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import data_fetcher
import features

def test_fetch_and_save_yfinance(tmp_path):
    # Mock yfinance download to return a simple DataFrame
    mock_df = pd.DataFrame({
        'Open': [1, 2],
        'Close': [2, 3],
        'High': [2, 3],
        'Low': [1, 2],
        'Volume': [100, 200]
    }, index=pd.to_datetime(['2022-01-01', '2022-01-02']))
    with mock.patch('yfinance.download', return_value=mock_df):
        ticker = 'AAPL'
        start = '2022-01-01'
        end = '2022-01-03'
        save_dir = tmp_path
        file_path = data_fetcher.fetch_and_save_yfinance(ticker, start, end, str(save_dir))
        assert os.path.exists(file_path)
        # Check file content
        df_loaded = pd.read_csv(file_path, index_col=0, parse_dates=True)
        pd.testing.assert_frame_equal(df_loaded, mock_df)

def test_fetch_and_save_finnhub(tmp_path):
    # Mock API response
    mock_json = {
        's': 'ok',
        't': [1640995200, 1641081600],  # 2022-01-01, 2022-01-02
        'o': [1, 2],
        'h': [2, 3],
        'l': [1, 2],
        'c': [2, 3],
        'v': [100, 200]
    }
    mock_response = mock.Mock()
    mock_response.json.return_value = mock_json
    with mock.patch('requests.get', return_value=mock_response):
        with mock.patch.object(data_fetcher, 'get_env_variable', return_value='FAKE_KEY'):
            ticker = 'AAPL'
            start = '2022-01-01'
            end = '2022-01-03'
            save_dir = tmp_path
            file_path = data_fetcher.fetch_and_save_finnhub(ticker, start, end, str(save_dir))
            assert os.path.exists(file_path)
            df_loaded = pd.read_csv(file_path)
            assert list(df_loaded.columns) == ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            assert len(df_loaded) == 2

def test_add_indicators(tmp_path):
    # Create a small DataFrame and save as CSV
    df = pd.DataFrame({
        'Date': pd.date_range('2022-01-01', periods=20, freq='D'),
        'Open': range(20),
        'High': range(1, 21),
        'Low': range(0, 20),
        'Close': range(2, 22),
        'Volume': [100]*20
    })
    input_csv = tmp_path / 'input.csv'
    output_csv = tmp_path / 'output.csv'
    df.to_csv(input_csv, index=False)
    features.process_and_save_with_indicators(str(input_csv), str(output_csv), sma_window=5, rsi_window=5, ema_window=5, forward_days=5, drop_na=True)
    df_out = pd.read_csv(output_csv)
    assert 'SMA' in df_out.columns
    assert 'RSI' in df_out.columns
    assert 'EMA' in df_out.columns
    assert 'target_return' in df_out.columns
    # Check that there are no NA values after drop_na
    assert not df_out.isna().any().any()

def test_train_xgboost_regressor(tmp_path):
    # Create a small processed DataFrame
    df = pd.DataFrame({
        'SMA': range(20),
        'RSI': range(1, 21),
        'EMA': range(2, 22),
        'target_return': [0.01 * i for i in range(20)]
    })
    input_csv = tmp_path / 'processed.csv'
    model_path = tmp_path / 'model.pkl'
    df.to_csv(input_csv, index=False)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
    import train_model
    score = train_model.train_xgboost_regressor(str(input_csv), str(model_path))
    assert os.path.exists(model_path)
    assert isinstance(score, float)

def test_apply_classification_thresholds():
    import train_model
    df = pd.DataFrame({
        'target_return': [-0.1, 0.0, 0.2]
    })
    df_labeled = train_model.apply_classification_thresholds(df, threshold=0.0)
    assert (df_labeled['label'] == [0, 1, 1]).all()

def test_cli_save_labeled_csv(tmp_path):
    import subprocess
    import sys
    import pandas as pd
    df = pd.DataFrame({
        'SMA': [1, 2],
        'RSI': [1, 2],
        'EMA': [1, 2],
        'target_return': [-0.1, 0.2]
    })
    input_csv = tmp_path / 'processed.csv'
    model_path = tmp_path / 'model.pkl'
    labeled_csv = tmp_path / 'labeled.csv'
    df.to_csv(input_csv, index=False)
    # Run CLI to save labeled CSV
    result = subprocess.run([
        sys.executable, os.path.join(os.path.dirname(__file__), '../src/train_model.py'),
        str(input_csv), str(model_path),
        '--save_labeled_csv', str(labeled_csv),
        '--threshold', '0.0'
    ], capture_output=True, text=True)
    assert os.path.exists(labeled_csv)
    df_labeled = pd.read_csv(labeled_csv)
    assert (df_labeled['label'] == [0, 1]).all()

def test_predictor(tmp_path):
    # Create a small processed DataFrame and train a model
    import train_model
    import predictor
    df = pd.DataFrame({
        'SMA': [1, 2, 3, 4, 5],
        'RSI': [2, 3, 4, 5, 6],
        'EMA': [3, 4, 5, 6, 7],
        'target_return': [0.1, -0.2, 0.3, -0.4, 0.5]
    })
    input_csv = tmp_path / 'input.csv'
    model_path = tmp_path / 'model.pkl'
    pred_csv = tmp_path / 'pred.csv'
    df.to_csv(input_csv, index=False)
    train_model.train_xgboost_regressor(str(input_csv), str(model_path))
    # Run prediction
    model = predictor.load_model(str(model_path))
    df_pred = predictor.predict_returns(model, str(input_csv))
    df_pred = predictor.apply_label(df_pred, threshold=0.0)
    assert 'predicted_return' in df_pred.columns
    assert 'predicted_label' in df_pred.columns
    # CLI test
    import subprocess
    import sys
    result = subprocess.run([
        sys.executable, os.path.join(os.path.dirname(__file__), '../src/predictor.py'),
        str(model_path), str(input_csv), str(pred_csv), '--threshold', '0.0'
    ], capture_output=True, text=True)
    assert os.path.exists(pred_csv)
    df_cli = pd.read_csv(pred_csv)
    assert 'predicted_return' in df_cli.columns
    assert 'predicted_label' in df_cli.columns 