#!/usr/bin/env python3
"""
Test script to verify the fundamental data fetching fix
"""

import os
import sys
import tempfile
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_fundamental_fix():
    """Test the fundamental data fetching with the fix."""
    
    ticker = "AAPL"
    
    print(f"Testing fundamental data fetching for {ticker}")
    print("=" * 50)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        # Import the fixed module
        from fundamental_fetcher import fetch_and_save_fundamentals
        
        # Test the function
        print("1. Testing fetch_and_save_fundamentals...")
        ratios_file = fetch_and_save_fundamentals(ticker, temp_dir)
        
        if ratios_file and os.path.exists(ratios_file):
            print(f"✅ Success! Ratios file created: {ratios_file}")
            
            # Load and display the ratios
            ratios_df = pd.read_csv(ratios_file)
            print(f"✅ Ratios loaded successfully: {len(ratios_df)} rows, {len(ratios_df.columns)} columns")
            
            # Show available columns
            print("\nAvailable fundamental metrics:")
            for col in ratios_df.columns:
                if col not in ['ticker', 'date']:
                    value = ratios_df[col].iloc[0]
                    print(f"  {col}: {value}")
            
            # Check for key metrics
            key_metrics = ['pe_ratio', 'pb_ratio', 'debt_to_equity', 'current_ratio', 'roe', 'roa']
            found_metrics = []
            for metric in key_metrics:
                if metric in ratios_df.columns:
                    found_metrics.append(metric)
            
            print(f"\n✅ Found {len(found_metrics)} key metrics: {found_metrics}")
            
            return True
            
        else:
            print("❌ Failed to create ratios file")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_features():
    """Test the enhanced features with fundamental data."""
    
    ticker = "AAPL"
    
    print(f"\nTesting enhanced features for {ticker}")
    print("=" * 50)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Import modules
        from data_fetcher import fetch_and_save_yfinance
        from enhanced_features import create_comprehensive_feature_set
        
        # Fetch price data
        print("1. Fetching price data...")
        price_file = fetch_and_save_yfinance(ticker, "2023-01-01", "2024-01-01", save_dir=temp_dir)
        
        if not os.path.exists(price_file):
            print("❌ Failed to fetch price data")
            return False
        
        print(f"✅ Price data fetched: {price_file}")
        
        # Create comprehensive features
        print("2. Creating comprehensive features...")
        output_csv = os.path.join(temp_dir, f"{ticker}_comprehensive.csv")
        
        comprehensive_df = create_comprehensive_feature_set(
            ticker=ticker,
            price_csv=price_file,
            fundamentals_dir=os.path.join(temp_dir, 'fundamentals'),
            output_csv=output_csv
        )
        
        if len(comprehensive_df) > 0:
            print(f"✅ Comprehensive features created: {len(comprehensive_df.columns)} columns, {len(comprehensive_df)} rows")
            
            # Show feature categories
            feature_cols = [col for col in comprehensive_df.columns if col not in ['Date', 'ticker', 'target_return']]
            
            technical_features = [col for col in feature_cols if col in ['SMA', 'RSI', 'EMA', 'daily_return', 'volatility_20d']]
            fundamental_features = [col for col in feature_cols if col in ['pe_ratio', 'pb_ratio', 'debt_to_equity', 'roe', 'roa']]
            
            print(f"  Technical features: {len(technical_features)}")
            print(f"  Fundamental features: {len(fundamental_features)}")
            print(f"  Total features: {len(feature_cols)}")
            
            return True
        else:
            print("❌ Failed to create comprehensive features")
            return False
            
    except Exception as e:
        print(f"❌ Error during enhanced features testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Fundamental Data Fetching Fix")
    print("=" * 60)
    
    # Test fundamental fetching
    fundamental_success = test_fundamental_fix()
    
    # Test enhanced features
    enhanced_success = test_enhanced_features()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"  Fundamental fetching: {'✅ PASS' if fundamental_success else '❌ FAIL'}")
    print(f"  Enhanced features: {'✅ PASS' if enhanced_success else '❌ FAIL'}")
    
    if fundamental_success and enhanced_success:
        print("\n🎉 All tests passed! The fix is working correctly.")
        print("You can now use the dashboard without the fundamental data error.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.") 