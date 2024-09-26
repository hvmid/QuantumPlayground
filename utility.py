import numpy as np
import pandas as pd
from dwave.system import DWaveSampler, EmbeddingComposite
import dimod
import yfinance as yf
import os
from scipy.optimize import minimize
import logging
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
# logging.basicConfig(level=logging.ERROR)

os.environ['DWAVE_API_TOKEN'] = 'DEV-e8972fd320fefdf057d6a44f51effd5a55f63141'


def fetch_data(ticker, period, interval):
    try:
        # Fetch the stock data
        stock = yf.Ticker(ticker)

        # Get historical market data
        hist = stock.history(period=period, interval=interval)
        hist.reset_index(inplace=True)

        # Get additional stock info
        info = stock.info

        # Extract the required metrics from the info dictionary
        extra_info = {
            'P/E': info.get('forwardPE', None),
            '52W_High': info.get('fiftyTwoWeekHigh', None),
            '52W_Low': info.get('fiftyTwoWeekLow', None),
            'Market_Cap': info.get('marketCap', None),
            'Bid': info.get('bid', None),
            'Ask': info.get('ask', None),
        }

        # Add the additional metrics as new columns to the historical DataFrame
        for column, value in extra_info.items():
            hist[column] = value

        hist.drop(columns=['Stock Splits'], inplace=True)
        return hist

    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {str(e)}")
        return None


def generate_signal_basic(df):
    # Buy if Close is below the previous day's Close; Sell if it's higher
    buy_signals = df['Close'] <= df['Close'].shift(1)
    sell_signals = df['Close'] > df['Close'].shift(1)
    return buy_signals, sell_signals

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

def backtest_basic(df, signals, initial_cash=100):
    cash = initial_cash  # Starting cash
    stock = 0  # Starting with no stock
    holdings_value = []  # Track portfolio value over time
    roi = []
    buy_hold = []

    initial_price = df['Close'].iloc[0]
    initial_shares = initial_cash / initial_price

    for i in range(len(signals)):
        price = df['Close'].iloc[i]
        signal = signals[i]

        if signal == 'Buy' and cash > 0:
            # Buy with all available cash
            stock += cash / price
            cash = 0
        elif signal == 'Sell' and stock > 0:
            # Sell all stock and convert to cash
            cash += stock * price
            stock = 0

        # Total value = cash + value of current stock holdings
        total_value = cash + stock * price
        holdings_value.append(total_value)

        # Calculate ROI
        roi_percent = ((total_value - initial_cash) / initial_cash) * 100
        roi.append(roi_percent)

        # Calculate buy-and-hold value
        buy_hold_value = initial_shares * price
        buy_hold_roi = ((buy_hold_value - initial_cash) / initial_cash) * 100
        buy_hold.append(buy_hold_roi)

    # Create a DataFrame to track portfolio value over time
    result_df = pd.DataFrame({
        'Date': df['Datetime'],
        'Portfolio Value': holdings_value,
        'roi': roi,
        'buy_hold': buy_hold
    })
    return result_df


def qubo_basic(buy_signals, sell_signals, df):
  # Create a QUBO model based on buy/sell signals
  Q = {}
  for i in range(len(df)):
      if buy_signals[i]:
          Q[(i, i)] = -1  # Encourage buy
      if sell_signals[i]:
          Q[(i, i)] = 1   # Encourage sell

  # Convert the QUBO to a Binary Quadratic Model (BQM)
  bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
  return bqm


def dwave_sampler_basic(bqm, num_reads):
  # Initialize the D-Wave sampler
  sampler = EmbeddingComposite(DWaveSampler())
  
  # Sample using D-Wave's quantum annealer
  sampleset = sampler.sample(bqm, num_reads=num_reads)
  
  # Map the results to buy/sell decisions
  decisions = []
  for _, sample in sampleset.first.sample.items():
      if sample == 1:
          decisions.append("Sell")
      else:
          decisions.append("Buy")
  return decisions


def calculate_outperformance(results, benchmark_results):
    final_roi = results['roi'].iloc[-1]
    benchmark_roi = benchmark_results['roi'].iloc[-1]
    if benchmark_roi != 0:
        return (final_roi - benchmark_roi) / abs(benchmark_roi)
    else:
        return float('inf') if final_roi > 0 else float('-inf') if final_roi < 0 else 0