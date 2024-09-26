from utility import *
import argparse
import ast
import matplotlib.pyplot as plt

def run_comparison(ticker, interval, period):
    # Convert period to yfinance format
    if period == 'last_month':
        period = '1mo'
    elif period == 'last_three_months':
        period = '3mo'

    df = fetch_data(ticker, period, interval)

    buy_signals, sell_signals = generate_signal_basic(df)

    df_test = df.drop([0]).rename(columns={'Date': 'Datetime'})

    # Classical approach
    classical_decisions = classical_optimization(buy_signals, sell_signals, df_test)
    classical_results = backtest_basic(df_test, classical_decisions)

    # Quantum approach
    bqm = qubo_basic(buy_signals, sell_signals, df)
    quantum_decisions = dwave_sampler_basic(bqm, 200)
    quantum_results = backtest_basic(df_test, quantum_decisions)

    return classical_results, quantum_results


def plot_results(classical_results, quantum_results, plot_dir, ticker, interval, period):
    plt.figure(figsize=(12, 8))
    plt.plot(classical_results['Date'], classical_results['roi'], label='Classical')
    plt.plot(quantum_results['Date'], quantum_results['roi'], label='Quantum')
    plt.plot(classical_results['Date'], classical_results['buy_hold'], label='Buy and Hold')
    plt.xlabel('Date')
    plt.ylabel('ROI (%)')
    plt.title(f'ROI Comparison: {ticker} ({interval}, {period})')
    plt.legend()

    plt.tight_layout()

    # Determine which approach performed better
    classical_final_roi = classical_results['roi'].iloc[-1]
    quantum_final_roi = quantum_results['roi'].iloc[-1]

    if quantum_final_roi > classical_final_roi:
        folder = "quantum"
    else:
        folder = "classical"

    # Create the folder if it doesn't exist
    full_path = os.path.join(plot_dir, folder)
    os.makedirs(full_path, exist_ok=True)

    plt.savefig(os.path.join(full_path, f'comparison_{ticker}_{interval}_{period}.png'))
    plt.close()

    return quantum_final_roi > classical_final_roi


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run quantum vs classical trading comparison')
    parser.add_argument('--stocks', type=str, default="['FFIE', 'SERV', 'SPY', 'INTC', 'NVDA', 'AXP']",
                        help='List of stock tickers (default: ["FFIE", "SERV", "SPY", "INTC", "NVDA", "AXP"])')
    parser.add_argument('--intervals', type=str, default="['1h', '1d']",
                        help='List of intervals (default: ["1h", "1d"])')
    parser.add_argument('--periods', type=str, default="['1y', 'last_month', '2y', 'last_three_months']",
                        help='List of periods (default: ["1y", "last_month", "2y", "last_three_months"])')
    parser.add_argument('--plot_dir', type=str, default="C:/sources/QuantumPlayground/plots",
                        help='Directory to save plots (default: C:/sources/QuantumPlayground/plots)')
    args = parser.parse_args()

    # Convert string representations of lists to actual lists
    stocks = ast.literal_eval(args.stocks)
    intervals = ast.literal_eval(args.intervals)
    periods = ast.literal_eval(args.periods)

    return stocks, intervals, periods, args.plot_dir


if __name__ == "__main__":
    stocks, intervals, periods, plot_dir = parse_arguments()

    # Create the main plot directory if it doesn't exist
    os.makedirs(plot_dir, exist_ok=True)

    quantum_wins = 0
    classical_wins = 0
    buy_hold_wins = 0
    total_runs = 0
    quantum_outperformance_classical = []
    quantum_outperformance_buy_hold = []
    classical_outperformance_buy_hold = []
    quantum_sharpe_ratios = []
    classical_sharpe_ratios = []
    buy_hold_sharpe_ratios = []

    for stock in stocks:
        for interval in intervals:
            for period in periods:
                try:
                    print(f"Processing: {stock} - {interval} - {period}")
                    classical_results, quantum_results = run_comparison(stock, interval, period)
                    if classical_results is None or quantum_results is None:
                        print(f"Skipping {stock} - {interval} - {period} due to error")
                        continue

                    total_runs += 1
                    classical_roi = classical_results['roi'].iloc[-1]
                    quantum_roi = quantum_results['roi'].iloc[-1]
                    buy_hold_roi = classical_results['buy_hold'].iloc[-1]

                    # Determine the winner
                    if quantum_roi > classical_roi and quantum_roi > buy_hold_roi:
                        quantum_wins += 1
                        print(f"Quantum outperformed for {stock} - {interval} - {period}")
                    elif classical_roi > quantum_roi and classical_roi > buy_hold_roi:
                        classical_wins += 1
                        print(f"Classical outperformed for {stock} - {interval} - {period}")
                    else:
                        buy_hold_wins += 1
                        print(f"Buy and Hold outperformed for {stock} - {interval} - {period}")

                    # Calculate outperformance factors
                    quantum_outperformance_classical.append(
                        calculate_outperformance(quantum_results, classical_results))
                    quantum_outperformance_buy_hold.append(calculate_outperformance(quantum_results, classical_results))
                    classical_outperformance_buy_hold.append(
                        calculate_outperformance(classical_results, quantum_results))

                    # Calculate Sharpe ratios (assuming risk-free rate of 0 for simplicity)
                    quantum_returns = quantum_results['roi'].pct_change().dropna()
                    classical_returns = classical_results['roi'].pct_change().dropna()
                    buy_hold_returns = classical_results['buy_hold'].pct_change().dropna()

                    quantum_sharpe_ratios.append(np.sqrt(252) * quantum_returns.mean() / quantum_returns.std())
                    classical_sharpe_ratios.append(np.sqrt(252) * classical_returns.mean() / classical_returns.std())
                    buy_hold_sharpe_ratios.append(np.sqrt(252) * buy_hold_returns.mean() / buy_hold_returns.std())

                    plot_results(classical_results, quantum_results, plot_dir, stock, interval, period)
                    print(f"Completed: {stock} - {interval} - {period}")
                except Exception as e:
                    print(f"Error processing {stock} - {interval} - {period}: {str(e)}")

    # Print final statistics
    print("\n--- Final Statistics ---")
    print(f"Total runs: {total_runs}")
    print(f"Quantum wins: {quantum_wins} ({quantum_wins / total_runs:.2%})")
    print(f"Classical wins: {classical_wins} ({classical_wins / total_runs:.2%})")
    print(f"Buy and Hold wins: {buy_hold_wins} ({buy_hold_wins / total_runs:.2%})")

    print("\nOutperformance Factors (average):")
    print(f"Quantum vs Classical: {np.mean(quantum_outperformance_classical):.2f}")
    print(f"Quantum vs Buy and Hold: {np.mean(quantum_outperformance_buy_hold):.2f}")
    print(f"Classical vs Buy and Hold: {np.mean(classical_outperformance_buy_hold):.2f}")

    print("\nSharpe Ratios (average):")
    print(f"Quantum: {np.mean(quantum_sharpe_ratios):.2f}")
    print(f"Classical: {np.mean(classical_sharpe_ratios):.2f}")
    print(f"Buy and Hold: {np.mean(buy_hold_sharpe_ratios):.2f}")

    print("\nBest Performing Combinations:")
    best_quantum = max(quantum_outperformance_classical)
    best_classical = max(classical_outperformance_buy_hold)
    print(f"Best Quantum outperformance vs Classical: {best_quantum:.2f}")
    print(f"Best Classical outperformance vs Buy and Hold: {best_classical:.2f}")

    print(f"\nPlots saved in: {plot_dir}")
