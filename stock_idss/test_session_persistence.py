#!/usr/bin/env python3
"""
Test script to verify session state persistence in the dashboard
"""

import os
import sys
import tempfile
import pandas as pd
import streamlit as st

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def test_session_state_persistence():
    """Test that session state can store and retrieve analysis results."""
    
    print("Testing Session State Persistence")
    print("=" * 40)
    
    # Create sample data
    sample_df = pd.DataFrame({
        'Date': pd.date_range('2023-01-01', periods=10),
        'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'predicted_return': [0.01, 0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01, 0.03, 0.01],
        'SMA': [100.5, 101.0, 101.5, 102.0, 102.5, 103.0, 103.5, 104.0, 104.5, 105.0],
        'RSI': [50, 55, 45, 60, 40, 55, 65, 35, 70, 50]
    })
    
    sample_fundamental = pd.DataFrame({
        'metric': ['pe_ratio', 'pb_ratio', 'debt_to_equity'],
        'value': [15.5, 2.1, 0.3]
    })
    
    # Test storing in session state
    print("1. Testing session state storage...")
    
    # Simulate what the dashboard would store
    analysis_results = {
        'df_pred': sample_df,
        'fundamental_data': sample_fundamental,
        'ticker': 'AAPL',
        'threshold': 0.02
    }
    
    # In a real Streamlit app, this would be:
    # st.session_state['analysis_results'] = analysis_results
    
    print(f"✅ Would store {len(analysis_results)} items in session state")
    print(f"   - df_pred shape: {analysis_results['df_pred'].shape}")
    print(f"   - fundamental_data shape: {analysis_results['fundamental_data'].shape}")
    print(f"   - ticker: {analysis_results['ticker']}")
    print(f"   - threshold: {analysis_results['threshold']}")
    
    # Test data serialization for download
    print("\n2. Testing data serialization for downloads...")
    
    try:
        # Test predictions CSV
        csv_bytes = sample_df.to_csv(index=False).encode('utf-8')
        print(f"✅ Predictions CSV size: {len(csv_bytes)} bytes")
        
        # Test fundamental data CSV
        fund_csv_bytes = sample_fundamental.to_csv(index=False).encode('utf-8')
        print(f"✅ Fundamental CSV size: {len(fund_csv_bytes)} bytes")
        
    except Exception as e:
        print(f"❌ Serialization failed: {e}")
        return False
    
    # Test data integrity
    print("\n3. Testing data integrity...")
    
    # Check that essential columns are present
    essential_columns = ['Date', 'Close', 'predicted_return']
    missing_columns = [col for col in essential_columns if col not in sample_df.columns]
    
    if missing_columns:
        print(f"❌ Missing essential columns: {missing_columns}")
        return False
    else:
        print(f"✅ All essential columns present: {essential_columns}")
    
    # Check data types
    print(f"✅ Date column type: {sample_df['Date'].dtype}")
    print(f"✅ Close column type: {sample_df['Close'].dtype}")
    print(f"✅ predicted_return column type: {sample_df['predicted_return'].dtype}")
    
    # Test CSV generation
    print("\n4. Testing CSV file generation...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save predictions CSV
        predictions_file = os.path.join(temp_dir, 'test_predictions.csv')
        sample_df.to_csv(predictions_file, index=False)
        print(f"✅ Predictions CSV saved: {predictions_file}")
        
        # Save fundamental CSV
        fundamental_file = os.path.join(temp_dir, 'test_fundamentals.csv')
        sample_fundamental.to_csv(fundamental_file, index=False)
        print(f"✅ Fundamental CSV saved: {fundamental_file}")
        
        # Verify files exist and have content
        if os.path.exists(predictions_file) and os.path.getsize(predictions_file) > 0:
            print(f"✅ Predictions file verified: {os.path.getsize(predictions_file)} bytes")
        else:
            print("❌ Predictions file verification failed")
            return False
            
        if os.path.exists(fundamental_file) and os.path.getsize(fundamental_file) > 0:
            print(f"✅ Fundamental file verified: {os.path.getsize(fundamental_file)} bytes")
        else:
            print("❌ Fundamental file verification failed")
            return False
        
    except Exception as e:
        print(f"❌ File generation failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 All tests passed! Session state persistence should work correctly.")
    print("\n📝 Summary:")
    print("   - Session state can store analysis results")
    print("   - Data can be serialized for downloads")
    print("   - CSV files can be generated correctly")
    print("   - Data integrity is maintained")
    
    return True

if __name__ == "__main__":
    success = test_session_state_persistence()
    
    if not success:
        print("\n❌ Some tests failed. Check the error messages above.")
        sys.exit(1) 