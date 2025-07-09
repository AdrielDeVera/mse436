#!/usr/bin/env python3
"""
Test script for fundamental features implementation.
This script demonstrates the complete fundamental features pipeline.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_fundamental_features():
    """Test the fundamental features implementation with AAPL."""
    
    ticker = "AAPL"
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    
    print(f"=== Testing Fundamental Features for {ticker} ===")
    print(f"Date range: {start_date} to {end_date}")
    print()
    
    # Create test directories
    test_dir = "test_output"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # 1. Test fundamental data fetching
        print("1. Testing fundamental data fetching...")
        from fundamental_fetcher import fetch_and_save_fundamentals
        
        fundamentals_dir = os.path.join(test_dir, "fundamentals")
        ratios_file = fetch_and_save_fundamentals(ticker, fundamentals_dir)
        
        if ratios_file and os.path.exists(ratios_file):
            ratios_df = pd.read_csv(ratios_file)
            print(f"✓ Fundamental data fetched successfully")
            print(f"  Ratios file: {ratios_file}")
            print(f"  Available ratios: {list(ratios_df.columns)}")
            
            # Show some key ratios
            print("\n  Key Financial Ratios:")
            for col in ['pe_ratio', 'pb_ratio', 'debt_to_equity', 'current_ratio', 'roe', 'roa']:
                if col in ratios_df.columns:
                    value = ratios_df[col].iloc[0]
                    print(f"    {col}: {value}")
        else:
            print("✗ Failed to fetch fundamental data")
            return False
        
        # 2. Test price data fetching
        print("\n2. Testing price data fetching...")
        from data_fetcher import fetch_and_save_yfinance
        
        price_file = fetch_and_save_yfinance(ticker, start_date, end_date, save_dir=test_dir)
        
        if os.path.exists(price_file):
            price_df = pd.read_csv(price_file)
            print(f"✓ Price data fetched successfully")
            print(f"  Price file: {price_file}")
            print(f"  Data points: {len(price_df)}")
        else:
            print("✗ Failed to fetch price data")
            return False
        
        # 3. Test comprehensive feature creation
        print("\n3. Testing comprehensive feature creation...")
        from enhanced_features import create_comprehensive_feature_set
        
        output_csv = os.path.join(test_dir, f"{ticker}_comprehensive_features.csv")
        comprehensive_df = create_comprehensive_feature_set(
            ticker=ticker,
            price_csv=price_file,
            fundamentals_dir=fundamentals_dir,
            output_csv=output_csv
        )
        
        if len(comprehensive_df) > 0:
            print(f"✓ Comprehensive features created successfully")
            print(f"  Output file: {output_csv}")
            print(f"  Total features: {len(comprehensive_df.columns)}")
            print(f"  Data points: {len(comprehensive_df)}")
            
            # Show feature summary
            feature_cols = [col for col in comprehensive_df.columns 
                          if col not in ['Date', 'ticker', 'target_return']]
            print(f"  Feature columns: {feature_cols}")
            
            # Show data types
            print("\n  Feature Data Types:")
            for col in feature_cols[:10]:  # Show first 10
                dtype = comprehensive_df[col].dtype
                missing_pct = (comprehensive_df[col].isna().sum() / len(comprehensive_df)) * 100
                print(f"    {col}: {dtype} (missing: {missing_pct:.1f}%)")
            
        else:
            print("✗ Failed to create comprehensive features")
            return False
        
        # 4. Test model training with fundamental features
        print("\n4. Testing model training with fundamental features...")
        from train_model import train_xgboost_regressor
        
        model_path = os.path.join(test_dir, f"{ticker}_model_with_fundamentals.pkl")
        test_score = train_xgboost_regressor(output_csv, model_path)
        
        print(f"✓ Model trained successfully")
        print(f"  Model file: {model_path}")
        print(f"  Test R² score: {test_score:.4f}")
        
        # 5. Test prediction with fundamental features
        print("\n5. Testing prediction with fundamental features...")
        from predictor import load_model, predict_returns
        
        model_data = load_model(model_path)
        predictions_df = predict_returns(model_data, output_csv)
        
        print(f"✓ Predictions made successfully")
        print(f"  Features used: {predictions_df['features_used'].iloc[0]}")
        print(f"  Features missing: {predictions_df['features_missing'].iloc[0]}")
        
        # Show prediction summary
        pred_summary = predictions_df[['predicted_return', 'predicted_label']].describe()
        print(f"\n  Prediction Summary:")
        print(pred_summary)
        
        # 6. Compare with basic features
        print("\n6. Comparing with basic features...")
        from features import process_and_save_with_indicators
        
        basic_output = os.path.join(test_dir, f"{ticker}_basic_features.csv")
        process_and_save_with_indicators(price_file, basic_output)
        
        basic_model_path = os.path.join(test_dir, f"{ticker}_basic_model.pkl")
        basic_score = train_xgboost_regressor(basic_output, basic_model_path)
        
        print(f"  Basic features R²: {basic_score:.4f}")
        print(f"  Fundamental features R²: {test_score:.4f}")
        print(f"  Improvement: {((test_score - basic_score) / basic_score * 100):.1f}%" if basic_score > 0 else "N/A")
        
        print(f"\n=== Test completed successfully! ===")
        print(f"All output files saved to: {test_dir}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_feature_comparison():
    """Show a comparison of available features."""
    
    print("\n=== Feature Comparison ===")
    
    basic_features = [
        'SMA', 'RSI', 'EMA'
    ]
    
    fundamental_features = [
        # Financial Ratios
        'pe_ratio', 'pb_ratio', 'debt_to_equity', 'current_ratio', 'roe', 'roa',
        
        # Growth Metrics
        'revenue_growth_yoy', 'earnings_growth_yoy',
        
        # Market Metrics
        'market_cap', 'enterprise_value',
        
        # Categorical (encoded)
        'market_cap_category_encoded', 'sector_code_encoded'
    ]
    
    advanced_technical = [
        'daily_return', 'volatility_20d', 'volatility_60d',
        'momentum_5d', 'momentum_20d', 'momentum_60d', 'volume_ratio',
        'price_vs_sma_20', 'price_vs_ema_20', 'bb_position'
    ]
    
    print(f"Basic Technical Features ({len(basic_features)}):")
    for feature in basic_features:
        print(f"  - {feature}")
    
    print(f"\nFundamental Features ({len(fundamental_features)}):")
    for feature in fundamental_features:
        print(f"  - {feature}")
    
    print(f"\nAdvanced Technical Features ({len(advanced_technical)}):")
    for feature in advanced_technical:
        print(f"  - {feature}")
    
    total_features = len(basic_features) + len(fundamental_features) + len(advanced_technical)
    print(f"\nTotal Features: {total_features}")
    print(f"Feature Expansion: {len(basic_features)} → {total_features} (+{total_features - len(basic_features)})")

if __name__ == "__main__":
    print("Stock IDSS - Fundamental Features Test")
    print("=" * 50)
    
    # Show feature comparison
    show_feature_comparison()
    
    # Run the test
    success = test_fundamental_features()
    
    if success:
        print("\n🎉 All tests passed! Fundamental features are working correctly.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
    
    print("\nTo use fundamental features in your pipeline:")
    print("python src/run_pipeline.py AAPL --start 2023-01-01 --end 2024-01-01")
    print("(Fundamental features are enabled by default)") 