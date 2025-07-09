#!/usr/bin/env python3
"""
Test script to verify that enhanced features include price data columns
"""

import os
import sys
import tempfile
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_price_data_inclusion():
    """Test that enhanced features include original price data."""
    
    ticker = "AAPL"
    
    print(f"Testing price data inclusion for {ticker}")
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
        
        # Check original price data columns
        original_df = pd.read_csv(price_file)
        print(f"✅ Original price data columns: {list(original_df.columns)}")
        
        # Create comprehensive features
        print("2. Creating comprehensive features...")
        output_csv = os.path.join(temp_dir, f"{ticker}_comprehensive.csv")
        
        comprehensive_df = create_comprehensive_feature_set(
            ticker=ticker,
            price_csv=price_file,
            fundamentals_dir=os.path.join(temp_dir, 'fundamentals'),
            output_csv=output_csv
        )
        
        print(f"✅ Comprehensive features created: {len(comprehensive_df.columns)} columns")
        print(f"Comprehensive features columns: {list(comprehensive_df.columns)}")
        
        # Check for essential price columns
        essential_columns = ['Date', 'Close', 'Volume']
        missing_columns = [col for col in essential_columns if col not in comprehensive_df.columns]
        
        if missing_columns:
            print(f"❌ Missing essential columns: {missing_columns}")
            return False
        else:
            print(f"✅ All essential columns present: {essential_columns}")
        
        # Check for technical indicators
        technical_columns = ['SMA', 'RSI', 'EMA']
        available_technical = [col for col in technical_columns if col in comprehensive_df.columns]
        print(f"✅ Available technical indicators: {available_technical}")
        
        # Check for fundamental features
        fundamental_columns = ['pe_ratio', 'pb_ratio', 'debt_to_equity']
        available_fundamental = [col for col in fundamental_columns if col in comprehensive_df.columns]
        print(f"✅ Available fundamental features: {available_fundamental}")
        
        # Show data summary
        print(f"\n📊 Data Summary:")
        print(f"  Rows: {len(comprehensive_df)}")
        print(f"  Columns: {len(comprehensive_df.columns)}")
        print(f"  Date range: {comprehensive_df['Date'].min()} to {comprehensive_df['Date'].max()}")
        
        if 'Close' in comprehensive_df.columns:
            print(f"  Close price range: ${comprehensive_df['Close'].min():.2f} to ${comprehensive_df['Close'].max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Price Data Inclusion in Enhanced Features")
    print("=" * 60)
    
    success = test_price_data_inclusion()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test passed! Enhanced features now include price data.")
        print("The dashboard technical indicators should work correctly.")
    else:
        print("❌ Test failed. Check the error messages above.") 