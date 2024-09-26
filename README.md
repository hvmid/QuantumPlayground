# Quantum vs Classical Trading Strategy Comparison

This project compares the performance of quantum-optimized, classically-optimized, and buy-and-hold trading strategies across various stocks, time intervals, and periods.

## Prerequisites

- Python 3.7+
- D-Wave Ocean SDK
- A D-Wave API token

## Installation

1. Clone this repository:

git clone https://github.com/yourusername/quantum-trading-comparison.git
cd quantum-trading-comparison
text

2. Create a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate
text

3. Install the required packages:

pip install -r requirements.txt
text

## Configuration

Set your D-Wave API token as an environment variable:

- On Unix-like systems (Linux, macOS):

export DWAVE_API_TOKEN=your-api-token-here
text

- On Windows:

set DWAVE_API_TOKEN=your-api-token-here
text

Alternatively, you can pass the API token as a command-line argument when running the script (see Usage section).

## Usage

Run the comparison script from the terminal:


python compare.py [--stocks STOCKS] [--intervals INTERVALS] [--periods PERIODS] [--plot_dir PLOT_DIR] [--api_token API_TOKEN]
text

Arguments:
- `--stocks`: List of stock tickers (default: "['FFIE', 'SERV', 'SPY', 'INTC', 'NVDA', 'AXP']")
- `--intervals`: List of time intervals (default: "['1h', '1d']")
- `--periods`: List of time periods (default: "['1y', 'last_month', '2y', 'last_three_months']")
- `--plot_dir`: Directory to save plots (default: "C:/sources/QuantumPlayground/plots")
- `--api_token`: D-Wave API token (optional, use if not set as environment variable)

Example:

python compare.py --stocks "['AAPL', 'GOOGL', 'MSFT']" --intervals "['1d', '1wk']" --periods "['1y', '2y']" --plot_dir "./plots"
text

## Output

### Terminal Output

The script will print progress updates for each stock-interval-period combination:


Processing: AAPL - 1d - 1y
Quantum outperformed for AAPL - 1d - 1y
Completed: AAPL - 1d - 1y
Processing: AAPL - 1d - 2y
Classical outperformed for AAPL - 1d - 2y
Completed: AAPL - 1d - 2y
...
text

At the end of the run, you'll see summary statistics:


--- Final Statistics ---
Total runs: 18
Quantum wins: 7 (38.89%)
Classical wins: 6 (33.33%)
Buy and Hold wins: 5 (27.78%)
Outperformance Factors (average):
Quantum vs Classical: 0.15
Quantum vs Buy and Hold: 0.22
Classical vs Buy and Hold: 0.08
Sharpe Ratios (average):
Quantum: 1.25
Classical: 1.18
Buy and Hold: 0.95
Best Performing Combinations:
Best Quantum outperformance vs Classical: 0.35
Best Classical outperformance vs Buy and Hold: 0.28
Plots saved in: ./plots
text

### Plots

The script generates comparison plots for each stock-interval-period combination. Plots are saved in the specified `plot_dir`, organized into "quantum" and "classical" subdirectories based on which approach performed better.

Each plot shows the ROI over time for the Quantum, Classical, and Buy-and-Hold strategies.

![comparison_SERV_1d_last_month](https://github.com/user-attachments/assets/04e4ae9a-dbdb-4396-981e-dc01411c4eb8)

## Potential Errors

1. **API Token Error**: If the D-Wave API token is not set or is invalid, you'll see an authentication error.

2. **Data Fetching Error**: If there's an issue fetching data for a particular stock, interval, or period, you'll see a message like:

Error processing AAPL - 1d - 1y: No data found, symbol may be delisted
text
The script will skip this combination and continue with the next.

3. **Quantum Solver Error**: If there's an issue with the D-Wave quantum solver, you might see errors related to the quantum annealing process.

4. **Memory Error**: For very large datasets or long time periods, you might encounter memory errors. Try reducing the number of stocks, shortening the time period, or using a machine with more RAM.

5. **Plot Directory Error**: If the script can't create or write to the specified plot directory, you'll see a permission error.

## Troubleshooting

- Ensure your D-Wave API token is correct and has the necessary permissions.
- Check your internet connection if you're having trouble fetching stock data.
- If you're getting quantum solver errors, try reducing the number of reads or the problem size.
- For memory errors, try processing fewer stocks or shorter time periods at once.

Project Link: [https://github.com/yourusername/quantum-trading-comparison](https://github.com/yourusername/quantum-trading-comparison)
