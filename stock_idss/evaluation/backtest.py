import pandas as pd
import numpy as np

def backtest_strategy(pred_csv: str, label_col='predicted_label', actual_col='target_return', initial_cash=1.0):
    df = pd.read_csv(pred_csv)
    # Assume: invest all if label==1, else hold cash
    df['strategy_return'] = np.where(df[label_col] == 1, df[actual_col], 0)
    df['cumulative_return'] = (1 + df['strategy_return']).cumprod() * initial_cash
    # Win/loss: did prediction sign match actual?
    df['win'] = np.sign(df[label_col] - 0.5) == np.sign(df[actual_col])
    win_rate = df['win'].mean()
    total_return = df['cumulative_return'].iloc[-1] / initial_cash - 1
    return_curve = df['cumulative_return']
    # Sharpe ratio (assume daily returns, risk-free rate 0)
    sharpe = df['strategy_return'].mean() / df['strategy_return'].std(ddof=0) * np.sqrt(252) if df['strategy_return'].std(ddof=0) > 0 else float('nan')
    return {
        'total_return': total_return,
        'win_rate': win_rate,
        'return_curve': return_curve,
        'sharpe': sharpe,
        'df': df
    }

if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser(description="Backtest predicted labels vs actual returns.")
    parser.add_argument("pred_csv", type=str, help="CSV with predicted_label and target_return")
    args = parser.parse_args()
    results = backtest_strategy(args.pred_csv)
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Win Rate: {results['win_rate']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe']:.2f}")
    # Plot return curve
    results['return_curve'].plot(title='Cumulative Return Curve')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Return')
    plt.show()
