import os
import pandas as pd
import pickle

def load_model(model_path: str):
    with open(model_path, 'rb') as f:
        return pickle.load(f)

def predict_returns(model, input_csv: str, features=None):
    if features is None:
        features = ['SMA', 'RSI', 'EMA']
    df = pd.read_csv(input_csv)
    preds = model.predict(df[features])
    df['predicted_return'] = preds
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
