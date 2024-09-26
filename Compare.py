from marketData import *
from utilityBasic import *
from scipy.optimize import minimize


os.environ['DWAVE_API_TOKEN'] = 'DEV-e8972fd320fefdf057d6a44f51effd5a55f63141'
def classical_optimization(buy_signals, sell_signals, df):
    def objective(x):
        decisions = ['Buy' if xi < 0.5 else 'Sell' for xi in x]
        results = backtest_basic(df, decisions)
        return -results['roi'].iloc[-1]  # Negative because we want to maximize ROI

    x0 = np.random.rand(len(df))
    bounds = [(0, 1) for _ in range(len(df))]

    result = minimize(objective, x0, method='L-BFGS-B', bounds=bounds)

    decisions = ['Buy' if xi < 0.5 else 'Sell' for xi in result.x]
    return decisions

# Fetch data
ticker = "FFIE"
df = fetch_data(ticker, '1y', '1h')

# Generate signals
buy_signals, sell_signals = generate_signal_basic(df)

# Classical optimization
classical_decisions = classical_optimization(buy_signals, sell_signals, df.drop([0]).rename(columns={'Date': 'Datetime'}))

# Backtest classical approach
classical_results = backtest_basic(df.drop([0]).rename(columns={'Date': 'Datetime'}), classical_decisions)

# Quantum approach (using your existing code)
bqm = qubo_basic(buy_signals, sell_signals, df)
quantum_decisions = dwave_sampler_basic(bqm, 200)
quantum_results = backtest_basic(df.drop([0]).rename(columns={'Date': 'Datetime'}), quantum_decisions)

# Compare results
print("Classical Approach Final ROI:", classical_results['roi'].iloc[-1])
print("Quantum Approach Final ROI:", quantum_results['roi'].iloc[-1])

if classical_results['roi'].iloc[-1] > quantum_results['roi'].iloc[-1]:
    print("The Classical approach performed better.")
else:
    print("The Quantum approach performed better.")

# Plot results for visualization
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(classical_results['Date'], classical_results['roi'], label='Classical')
plt.plot(quantum_results['Date'], quantum_results['roi'], label='Quantum')
plt.plot(classical_results['Date'], classical_results['buy_hold'], label='Buy and Hold')
plt.xlabel('Date')
plt.ylabel('ROI (%)')
plt.title('ROI Comparison: Classical vs Quantum vs Buy and Hold')
plt.legend()
plt.show()


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


def plot_results(ticker, interval, period, classical_results, quantum_results):
    plt.figure(figsize=(12, 8))
    plt.plot(classical_results['Date'], classical_results['roi'], label='Classical')
    plt.plot(quantum_results['Date'], quantum_results['roi'], label='Quantum')
    plt.plot(classical_results['Date'], classical_results['buy_hold'], label='Buy and Hold')
    plt.xlabel('Date')
    plt.ylabel('ROI (%)')
    plt.title(f'ROI Comparison: {ticker} ({interval}, {period})')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'C:/sources/QuantumPlayground/plots/comparison_{ticker}_{interval}_{period}.png')
    plt.close()


# Main execution
stocks = ['FFIE', 'SERV', 'SPY', 'INTC', 'NVDA', 'AXP']
intervals = ['1h', '1d']
periods = ['1y', 'last_month', '2y', 'last_three_months']

for stock in stocks:
    for interval in intervals:
        for period in periods:
            try:
                print(f"Processing: {stock} - {interval} - {period}")
                classical_results, quantum_results = run_comparison(stock, interval, period)
                plot_results(stock, interval, period, classical_results, quantum_results)
                print(f"Completed: {stock} - {interval} - {period}")
            except Exception as e:
                print(f"Error processing {stock} - {interval} - {period}: {str(e)}")

print("All comparisons completed.")