import os
import pandas as pd
import xgboost as xgb
import pickle

def train_xgboost_regressor(input_csv: str, model_path: str, features=None, target='target_return', test_size=0.2, random_state=42):
    if features is None:
        # Default features - will be expanded if fundamental data is available
        features = ['SMA', 'RSI', 'EMA']
    
    df = pd.read_csv(input_csv)
    
    # Dynamically determine available features
    available_features = []
    for feature in features:
        if feature in df.columns:
            available_features.append(feature)
    
    # Add fundamental features if available
    fundamental_features = [
        'pe_ratio', 'pb_ratio', 'debt_to_equity', 'current_ratio', 'roe', 'roa',
        'revenue_growth_yoy', 'earnings_growth_yoy', 'market_cap', 'enterprise_value',
        'market_cap_category_encoded', 'sector_code_encoded',
        'daily_return', 'volatility_20d', 'volatility_60d',
        'momentum_5d', 'momentum_20d', 'momentum_60d', 'volume_ratio',
        'price_vs_sma_20', 'price_vs_ema_20', 'bb_position'
    ]
    
    for feature in fundamental_features:
        if feature in df.columns and feature not in available_features:
            available_features.append(feature)
    
    print(f"Using features: {available_features}")
    print(f"Total features: {len(available_features)}")
    
    # Remove rows with missing values in features or target
    df_clean = df.dropna(subset=available_features + [target])
    print(f"Rows after removing NaN: {len(df_clean)}")
    
    X = df_clean[available_features]
    y = df_clean[target]
    
    # Simple train/test split
    split_idx = int(len(df_clean) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    model = xgb.XGBRegressor(random_state=random_state)
    model.fit(X_train, y_train)
    
    # Save model and feature list
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model_data = {
        'model': model,
        'features': available_features,
        'feature_importance': dict(zip(available_features, model.feature_importances_))
    }
    
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    # Calculate and print metrics
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Training R²: {train_score:.4f}")
    print(f"Test R²: {test_score:.4f}")
    
    # Print feature importance
    print("\nTop 10 Feature Importance:")
    importance_sorted = sorted(model_data['feature_importance'].items(), key=lambda x: x[1], reverse=True)
    for feature, importance in importance_sorted[:10]:
        print(f"  {feature}: {importance:.4f}")
    
    return test_score

def apply_classification_thresholds(df: pd.DataFrame, threshold=0.0, label_col='label', target_col='target_return') -> pd.DataFrame:
    df = df.copy()
    df[label_col] = (df[target_col] >= threshold).astype(int)
    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train XGBoost regressor on processed data.")
    parser.add_argument("input_csv", type=str, help="Processed CSV file path")
    parser.add_argument("model_path", type=str, default="../models/model.pkl", help="Path to save model")
    parser.add_argument("--test_size", type=float, default=0.2)
    parser.add_argument("--save_labeled_csv", type=str, default=None, help="If set, save a CSV with classification labels.")
    parser.add_argument("--threshold", type=float, default=0.0, help="Threshold for classification label.")
    args = parser.parse_args()
    score = train_xgboost_regressor(args.input_csv, args.model_path, test_size=args.test_size)
    print(f"Model saved to {args.model_path}. Test R^2: {score:.4f}")
    if args.save_labeled_csv:
        df = pd.read_csv(args.input_csv)
        df = apply_classification_thresholds(df, threshold=args.threshold)
        df.to_csv(args.save_labeled_csv, index=False)
        print(f"Labeled CSV saved to {args.save_labeled_csv}")
