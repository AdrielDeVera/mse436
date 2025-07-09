import os
import pandas as pd
import pickle

def load_model(model_path: str):
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    # Handle both old format (just model) and new format (dict with model and features)
    if isinstance(model_data, dict):
        return model_data
    else:
        # Old format - return dict with default features
        return {
            'model': model_data,
            'features': ['SMA', 'RSI', 'EMA'],
            'feature_importance': {}
        }

def predict_returns(model_data, input_csv: str, features=None):
    model = model_data['model']
    if features is None:
        features = model_data['features']
    
    df = pd.read_csv(input_csv)
    
    # Check which features are available
    available_features = [f for f in features if f in df.columns]
    missing_features = [f for f in features if f not in df.columns]
    
    if missing_features:
        print(f"Warning: Missing features: {missing_features}")
    
    if not available_features:
        raise ValueError("No features available for prediction")
    
    # Use only available features
    X = df[available_features]
    
    # Handle missing values
    if X.isna().any().any():
        print("Warning: Found NaN values in features, filling with 0")
        X = X.fillna(0)
    
    preds = model.predict(X)
    df['predicted_return'] = preds
    
    # Add feature availability info
    df['features_used'] = len(available_features)
    df['features_missing'] = len(missing_features)
    
    return df

def apply_label(df: pd.DataFrame, threshold=0.0, pred_col='predicted_return', label_col='predicted_label'):
    df = df.copy()
    df[label_col] = (df[pred_col] >= threshold).astype(int)
    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Predict returns and labels using trained model.")
    parser.add_argument("model_path", type=str, help="Path to trained model.pkl")
    parser.add_argument("input_csv", type=str, help="Input CSV with features")
    parser.add_argument("output_csv", type=str, help="Output CSV with predictions")
    parser.add_argument("--threshold", type=float, default=0.0, help="Threshold for predicted label")
    args = parser.parse_args()
    model = load_model(args.model_path)
    df_pred = predict_returns(model, args.input_csv)
    df_pred = apply_label(df_pred, threshold=args.threshold)
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    df_pred.to_csv(args.output_csv, index=False)
    print(f"Predictions saved to {args.output_csv}")
