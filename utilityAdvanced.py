import numpy as np
import pandas as pd
from dwave.system import DWaveSampler, EmbeddingComposite
import dimod
import yfinance as yf
import os
from marketData import *
from utilityBasic import *

def _calculate_confidence(rsi):
    if pd.isna(rsi):
        return 0  # Default to no confidence if RSI is NaN
    elif rsi <= 30:
        return 1  # Maximum confidence for oversold conditions
    elif rsi >= 70:
        return 0  # Minimum confidence for overbought conditions
    else:
        return max(min((70 - rsi) / 40, 1), 0)  

def _calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def _calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line


def generate_advanced_signal(df):
    # Calculate technical indicators
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['RSI'] = _calculate_rsi(df['Close'], 14)
    df['MACD'], df['Signal'] = _calculate_macd(df['Close'])
    
    # Generate signals based on multiple factors
    buy_signals = (df['Close'] > df['SMA20']) & (df['SMA20'] > df['SMA50']) & (df['RSI'] < 70) & (df['MACD'] > df['Signal'])
    sell_signals = (df['Close'] < df['SMA20']) & (df['SMA20'] < df['SMA50']) & (df['RSI'] > 30) & (df['MACD'] < df['Signal'])
    
    return buy_signals, sell_signals


def qubo_advanced(buy_signals, sell_signals, df):
  Q = {}
  for i in range(len(df)):
      if buy_signals[i]:
          Q[(i, i)] = -1 * (1 + df['RSI'].iloc[i] / 100)  # Stronger buy signal for lower RSI
      if sell_signals[i]:
          Q[(i, i)] = 1 * (1 + (100 - df['RSI'].iloc[i]) / 100)  # Stronger 
  bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
  return bqm


def dwave_sampler_advanced(bqm, num_reads):
  # Initialize the D-Wave sampler
  sampler = EmbeddingComposite(DWaveSampler())
  
  # Sample using D-Wave's quantum annealer
  sampleset = sampler.sample(bqm, num_reads=100)
  
  # Map the results to buy/sell decisions
  decisions = []
  for _, sample in sampleset.first.sample.items():
      if sample == 1:
          decisions.append("Sell")
      else:
          decisions.append("Buy")
  return decisions

def backtest(df, signals, initial_cash=100000, risk_per_trade=0.02):
    cash = initial_cash
    stock = 0
    holdings_value = []
    roi = []
    
    for i in range(len(signals)):
        if i >= len(df):
            break  # Exit the loop if we've reached the end of the DataFrame
        
        price = df['Close'].iloc[i]
        signal = signals[i]
        rsi = df['RSI'].iloc[i]
        confidence = _calculate_confidence(rsi)
        if signal == 'Buy' and cash > 0:
            confidence = min((70 - rsi) / 30, 1)
            trade_amount = min(cash * risk_per_trade * confidence, cash)
            shares_to_buy = trade_amount // price
            cash -= shares_to_buy * price
            stock += shares_to_buy
            print(confidence)
            print(trade_amount)
            print(shares_to_buy)
            print(stock)
        elif signal == 'Sell' and stock > 0:
            confidence = min((rsi - 30) / 30, 1)
            shares_to_sell = int(stock * risk_per_trade * confidence)
            cash += shares_to_sell * price
            stock -= shares_to_sell
        
        total_value = cash + stock * price
        roi_percent = ((total_value - initial_cash) / initial_cash) * 100
        holdings_value.append(total_value)
        roi.append(roi_percent)
        print(cash)
        print("---")
    result_df = pd.DataFrame({'Date': df['Date'][:len(holdings_value)], 'Portfolio Value': holdings_value, 'ROI': roi})
    return result_df
  