import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Import existing modules
try:
    from stock_idss.src.features import add_indicators, add_target_return, load_stock_csv
    from stock_idss.src.fundamental_fetcher import fetch_and_save_fundamentals, extract_key_ratios
except ModuleNotFoundError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
    from features import add_indicators, add_target_return, load_stock_csv
    from fundamental_fetcher import fetch_and_save_fundamentals, extract_key_ratios

def load_fundamental_ratios(ticker: str, fundamentals_dir: str = '../data/fundamentals/') -> pd.DataFrame:
    """
    Load fundamental ratios for a ticker.
    
    Args:
        ticker (str): Stock ticker symbol
        fundamentals_dir (str): Directory containing fundamental data
        
    Returns:
        pd.DataFrame: DataFrame with fundamental ratios
    """
    ratios_file = os.path.join(fundamentals_dir, f"{ticker}_ratios.csv")
    
    if os.path.exists(ratios_file):
        try:
            return pd.read_csv(ratios_file)
        except Exception as e:
            print(f"Error reading fundamental ratios for {ticker}: {e}")
            return pd.DataFrame()
    else:
        # Try to fetch fundamental data if not available
        print(f"Fundamental data not found for {ticker}. Fetching...")
        try:
            fetch_and_save_fundamentals(ticker, fundamentals_dir)
            
            if os.path.exists(ratios_file):
                return pd.read_csv(ratios_file)
            else:
                print(f"Could not fetch fundamental data for {ticker}")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error fetching fundamental data for {ticker}: {e}")
            return pd.DataFrame()

def create_fundamental_features(ratios_df: pd.DataFrame) -> Dict[str, float]:
    """
    Create feature dictionary from fundamental ratios.
    
    Args:
        ratios_df (pd.DataFrame): DataFrame with fundamental ratios
        
    Returns:
        Dict[str, float]: Dictionary of fundamental features
    """
    if ratios_df.empty:
        return {}
    
    # Get the first (and usually only) row
    row = ratios_df.iloc[0]
    
    features = {}
    
    # Financial Ratios
    features['pe_ratio'] = row.get('pe_ratio', np.nan)
    features['pb_ratio'] = row.get('pb_ratio', np.nan)
    features['debt_to_equity'] = row.get('debt_to_equity', np.nan)
    features['current_ratio'] = row.get('current_ratio', np.nan)
    features['roe'] = row.get('roe', np.nan)
    features['roa'] = row.get('roa', np.nan)
    
    # Growth Metrics
    features['revenue_growth_yoy'] = row.get('revenue_growth_yoy', np.nan)
    features['earnings_growth_yoy'] = row.get('earnings_growth_yoy', np.nan)
    
    # Market Metrics
    features['market_cap'] = row.get('market_cap', np.nan)
    features['enterprise_value'] = row.get('enterprise_value', np.nan)
    
    # Categorical features (will be encoded)
    features['market_cap_category'] = row.get('market_cap_category', 'Unknown')
    features['sector_classified'] = row.get('sector_classified', 'Unknown')
    features['sector_code'] = row.get('sector_code', 'UNK')
    
    return features

def encode_categorical_features(features: Dict[str, float]) -> Dict[str, float]:
    """
    Encode categorical features into numerical values.
    
    Args:
        features (Dict[str, float]): Dictionary of features including categorical ones
        
    Returns:
        Dict[str, float]: Dictionary with encoded categorical features
    """
    encoded_features = features.copy()
    
    # Market Cap Category encoding
    market_cap_mapping = {
        'Large': 3,
        'Mid': 2, 
        'Small': 1,
        'Unknown': 0
    }
    
    if 'market_cap_category' in encoded_features:
        encoded_features['market_cap_category_encoded'] = market_cap_mapping.get(
            encoded_features['market_cap_category'], 0
        )
    
    # Sector encoding (using sector codes)
    sector_mapping = {
        'TEC': 1,  # Technology
        'HEA': 2,  # Healthcare
        'FIN': 3,  # Financial
        'CON': 4,  # Consumer Discretionary
        'STA': 5,  # Consumer Staples
        'COM': 6,  # Communication Services
        'IND': 7,  # Industrials
        'ENE': 8,  # Energy
        'MAT': 9,  # Materials
        'REA': 10, # Real Estate
        'UTI': 11, # Utilities
        'UNK': 0   # Unknown
    }
    
    if 'sector_code' in encoded_features:
        encoded_features['sector_code_encoded'] = sector_mapping.get(
            encoded_features['sector_code'], 0
        )
    
    return encoded_features

def add_advanced_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add advanced technical indicators beyond basic SMA/RSI/EMA.
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        
    Returns:
        pd.DataFrame: DataFrame with additional technical features
    """
    df = df.copy()
    
    # Volatility measures
    df['daily_return'] = df['Close'].pct_change()
    df['volatility_20d'] = df['daily_return'].rolling(window=20).std()
    df['volatility_60d'] = df['daily_return'].rolling(window=60).std()
    
    # Price momentum
    df['momentum_5d'] = df['Close'] / df['Close'].shift(5) - 1
    df['momentum_20d'] = df['Close'] / df['Close'].shift(20) - 1
    df['momentum_60d'] = df['Close'] / df['Close'].shift(60) - 1
    
    # Volume indicators
    df['volume_sma_20'] = df['Volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['Volume'] / df['volume_sma_20']
    
    # Price relative to moving averages
    df['price_vs_sma_20'] = df['Close'] / df['SMA'] - 1
    df['price_vs_ema_20'] = df['Close'] / df['EMA'] - 1
    
    # Bollinger Bands (if pandas_ta is available)
    try:
        import pandas_ta as ta
        bb = ta.bbands(df['Close'], length=20)
        df['bb_upper'] = bb['BBU_20_2.0']
        df['bb_middle'] = bb['BBM_20_2.0']
        df['bb_lower'] = bb['BBL_20_2.0']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    except ImportError:
        print("pandas_ta not available, skipping Bollinger Bands")
    
    return df

def merge_fundamental_with_technical(technical_df: pd.DataFrame, fundamental_features: Dict[str, float], 
                                   ticker: str) -> pd.DataFrame:
    """
    Merge fundamental features with technical indicators.
    
    Args:
        technical_df (pd.DataFrame): DataFrame with technical indicators
        fundamental_features (Dict[str, float]): Dictionary of fundamental features
        ticker (str): Stock ticker symbol
        
    Returns:
        pd.DataFrame: Combined DataFrame with all features
    """
    df = technical_df.copy()
    
    # Encode categorical features
    encoded_features = encode_categorical_features(fundamental_features)
    
    # Add fundamental features to each row
    for feature_name, feature_value in encoded_features.items():
        if isinstance(feature_value, (int, float)) and not pd.isna(feature_value):
            df[feature_name] = feature_value
        elif isinstance(feature_value, str):
            # Keep categorical features as strings for now
            df[feature_name] = feature_value
    
    # Add ticker identifier
    df['ticker'] = ticker
    
    return df

def create_comprehensive_feature_set(ticker: str, price_csv: str, fundamentals_dir: str = '../data/fundamentals/',
                                   output_csv: str = None) -> pd.DataFrame:
    """
    Create comprehensive feature set combining technical and fundamental data.
    
    Args:
        ticker (str): Stock ticker symbol
        price_csv (str): Path to price data CSV
        fundamentals_dir (str): Directory containing fundamental data
        output_csv (str): Optional path to save the combined features
        
    Returns:
        pd.DataFrame: DataFrame with comprehensive feature set
    """
    # Load price data and add technical indicators
    df = load_stock_csv(price_csv)
    df = add_indicators(df)
    df = add_advanced_technical_features(df)
    df = add_target_return(df)
    
    # Load fundamental data
    ratios_df = load_fundamental_ratios(ticker, fundamentals_dir)
    fundamental_features = create_fundamental_features(ratios_df)
    
    # Merge technical and fundamental features
    combined_df = merge_fundamental_with_technical(df, fundamental_features, ticker)
    
    # Define feature columns (excluding target and metadata)
    feature_columns = [
        # Technical indicators
        'SMA', 'RSI', 'EMA', 'daily_return', 'volatility_20d', 'volatility_60d',
        'momentum_5d', 'momentum_20d', 'momentum_60d', 'volume_ratio',
        'price_vs_sma_20', 'price_vs_ema_20',
        
        # Fundamental ratios
        'pe_ratio', 'pb_ratio', 'debt_to_equity', 'current_ratio', 'roe', 'roa',
        'revenue_growth_yoy', 'earnings_growth_yoy', 'market_cap', 'enterprise_value',
        
        # Encoded categorical features
        'market_cap_category_encoded', 'sector_code_encoded'
    ]
    
    # Add Bollinger Bands if available
    if 'bb_position' in combined_df.columns:
        feature_columns.append('bb_position')
    
    # Filter to available features
    available_features = [col for col in feature_columns if col in combined_df.columns]
    
    # Create final feature set - include original price data for visualization
    price_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    available_price_columns = [col for col in price_columns if col in combined_df.columns]
    
    final_features = ['Date', 'ticker'] + available_price_columns + available_features + ['target_return']
    final_df = combined_df[final_features].copy()
    
    # Save if output path provided
    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        final_df.to_csv(output_csv, index=False)
        print(f"Comprehensive features saved to {output_csv}")
    
    return final_df

def get_feature_summary(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Get summary statistics for all features.
    
    Args:
        df (pd.DataFrame): DataFrame with features
        
    Returns:
        Dict[str, Dict[str, float]]: Summary statistics for each feature
    """
    # Separate numerical and categorical features
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    summary = {}
    
    # Numerical features
    for col in numerical_cols:
        if col not in ['Date', 'ticker', 'target_return']:
            summary[col] = {
                'mean': df[col].mean(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'missing_pct': (df[col].isna().sum() / len(df)) * 100
            }
    
    # Categorical features
    for col in categorical_cols:
        if col not in ['Date', 'ticker']:
            summary[col] = {
                'unique_values': df[col].nunique(),
                'most_common': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None,
                'missing_pct': (df[col].isna().sum() / len(df)) * 100
            }
    
    return summary

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create comprehensive feature set with technical and fundamental data.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol")
    parser.add_argument("price_csv", type=str, help="Path to price data CSV")
    parser.add_argument("--fundamentals_dir", type=str, default="../data/fundamentals/", help="Directory for fundamental data")
    parser.add_argument("--output_csv", type=str, help="Output CSV path")
    args = parser.parse_args()
    
    # Create comprehensive feature set
    df = create_comprehensive_feature_set(
        args.ticker, 
        args.price_csv, 
        args.fundamentals_dir,
        args.output_csv
    )
    
    # Print feature summary
    summary = get_feature_summary(df)
    print(f"\nFeature Summary for {args.ticker}:")
    for feature, stats in summary.items():
        print(f"\n{feature}:")
        for stat, value in stats.items():
            print(f"  {stat}: {value}")
    
    print(f"\nTotal features: {len(df.columns)}")
    print(f"Total rows: {len(df)}")
    print(f"Features with data: {len([col for col in df.columns if col not in ['Date', 'ticker', 'target_return']])}") 