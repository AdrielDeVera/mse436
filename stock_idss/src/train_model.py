import os
import pandas as pd
import xgboost as xgb
import pickle

def train_xgboost_regressor(input_csv: str, model_path: str, features=None, target='target_return', test_size=0.2, random_state=42):
    if features is None:
        features = ['SMA', 'RSI', 'EMA']
    df = pd.read_csv(input_csv)
    X = df[features]
    y = df[target]
    # Simple train/test split
    split_idx = int(len(df) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    model = xgb.XGBRegressor(random_state=random_state)
    model.fit(X_train, y_train)
    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    # Optionally return test score
    score = model.score(X_test, y_test)
    return score

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
