import yfinance as yf
import pandas as pd


def fetch_data(ticker='SPY', period='1y', interval='1h'):

  # Fetch the stock data
  stock = yf.Ticker(ticker)
  
  # Get historical market data (e.g., daily price data)
  hist = stock.history(period=period, interval=interval)  # Adjust period as needed
  hist.reset_index(inplace=True)  # Reset index to make Date a column
  
  # Get additional stock info
  info = stock.info
  
  # Extract the required metrics from the info dictionary
  extra_info = {
      'P/E': info.get('forwardPE', None),  # P/E Ratio (forward P/E)
      '52W_High': info.get('fiftyTwoWeekHigh', None),  # 52-week high
      '52W_Low': info.get('fiftyTwoWeekLow', None),  # 52-week low
      'Market_Cap': info.get('marketCap', None),  # Market capitalization
      'Bid': info.get('bid', None),  # Bid price
      'Ask': info.get('ask', None),  # Ask price
  }
  
  # Add the additional metrics as new columns to the historical DataFrame
  for column, value in extra_info.items():
      hist[column] = value
  
  hist.drop(columns=['Stock Splits'], inplace=True)
  return hist