import numpy as np
import pandas as pd
from dwave.system import DWaveSampler, EmbeddingComposite
import dimod
import yfinance as yf
import os
from marketData import *
from utilityBasic import *


def generate_signal_basic(df):
    # Buy if Close is below the previous day's Close; Sell if it's higher
    buy_signals = df['Close'] <= df['Close'].shift(1)
    sell_signals = df['Close'] > df['Close'].shift(1)
    return buy_signals, sell_signals

def backtest_basic(df, signals, initial_cash=100):
    cash = initial_cash  # Starting cash
    stock = 0            # Starting with no stock
    holdings_value = []   # Track portfolio value over time
    roi = []
    day1 = 0
    buy_hold = []
    
    for i in range(len(signals)):
        
        price = df['Close'].iloc[i]
        signal = signals[i]

        if i==0:
          day1 = cash / price

        if signal == 'Buy' and cash > 0:
            # Buy with all available cash
            stock = cash / price
            cash = 0

        elif signal == 'Sell' and stock > 0:
            # Sell all stock and convert to cash
            cash = stock * price
            stock = 0

        # Total value = cash + value of current stock holdings
        buy_hold.append(price*day1)
        total_value = cash + stock * price
        roi_percent = ((total_value-initial_cash)/initial_cash)*100
        holdings_value.append(total_value)
        roi.append(roi_percent)
    # Create a DataFrame to track portfolio value over time
    result_df = pd.DataFrame({'Date': df['Datetime'], 'Portfolio Value': holdings_value, 'roi':roi, 'buy_hold':buy_hold})
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
  