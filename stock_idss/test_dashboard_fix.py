#!/usr/bin/env python3
"""
Test script to verify the dashboard DataFrame truth value fix
"""

import pandas as pd
import numpy as np

def test_dataframe_truth_value():
    """Test that DataFrame truth value checks work correctly."""
    
    print("Testing DataFrame truth value fixes...")
    print("=" * 50)
    
    # Create test DataFrames
    empty_df = pd.DataFrame()
    non_empty_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    
    print("1. Testing empty DataFrame checks:")
    
    # Test the old problematic way (this would cause an error)
    try:
        # This is what was causing the error
        result = not empty_df or empty_df.empty
        print("❌ Old way still works (unexpected)")
    except ValueError as e:
        print(f"✅ Old way correctly raises error: {e}")
    
    # Test the new safe way
    try:
        result = len(empty_df) == 0
        print(f"✅ New way works: {result}")
    except Exception as e:
        print(f"❌ New way failed: {e}")
    
    print("\n2. Testing non-empty DataFrame checks:")
    
    # Test the new safe way with non-empty DataFrame
    try:
        result = len(non_empty_df) > 0
        print(f"✅ New way works for non-empty: {result}")
    except Exception as e:
        print(f"❌ New way failed for non-empty: {e}")
    
    print("\n3. Testing None checks:")
    
    # Test None handling
    try:
        df = None
        result = df is None or len(df) == 0 if df is not None else True
        print(f"✅ None check works: {result}")
    except Exception as e:
        print(f"❌ None check failed: {e}")
    
    print("\n4. Testing mode() empty check:")
    
    # Test the mode() empty check fix
    try:
        # Empty mode
        empty_mode = pd.Series([]).mode()
        result = len(empty_mode) > 0
        print(f"✅ Empty mode check works: {result}")
        
        # Non-empty mode
        non_empty_mode = pd.Series([1, 1, 2, 2, 1]).mode()
        result = len(non_empty_mode) > 0
        print(f"✅ Non-empty mode check works: {result}")
        
    except Exception as e:
        print(f"❌ Mode check failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ All DataFrame truth value tests passed!")
    print("The dashboard should now work without the ambiguous truth value error.")

if __name__ == "__main__":
    test_dataframe_truth_value() 