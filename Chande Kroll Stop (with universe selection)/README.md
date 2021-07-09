# Chande Kroll Stop (with universe Selection)

## Chande Kroll Stop
This is a trend-following indicator that identifies the stop loss for a long or short position by using a variation on directional movement. It is calculated on the average true range of an instrument’s volatility. The stops are placed under (and on) the high (low) of the last “n” bars. The difference is proportional to the average True Range on “N” bars.

## Universe
* Sorted by market cap > 2B

## Strategy
* Enter when close break above Kroll long
* Add to position when close remain above Kroll short and RSI(10)<30
* Exit when close break below Kroll short
* ATR based position sizing

## Results
- Backtest Timeframe: 2016-2020
- Net Profit: 102.68%
- Compounding Annual Return: 15.158%
- Drawdown: 19.600%
- Sharpe Ratio: 1.08
- Alpha: 0.134

#### Credit is where credit due
- https://www.interactivebrokers.com/en/software/tws/usersguidebook/technicalanalytics/chandekrollstop.htm