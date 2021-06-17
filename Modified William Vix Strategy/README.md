# Modified William Vix Strategyy

Chicago Board Options Exchange (CBOE) Volatility Index (VIX)  has become a very popular measure of market risk since it was introduced in 1993. The VIX, which is derived from the implied volatility of stock index options, is intended to represent traders’ expectations of volatility over the next 30 days. 

In this strategy, we look to hold long position in SPY when VIX is below 2 standard deviation and rotate capital to bond (TLT) when VIX exceeds 2 standard deviation is a rolling 22-day period. There is a wait out period before reassessing whether to re-enter long position in SPY. The wait out period is calculated based on the volatity of SPY.

- Backtest Timeframe: 2016-2020
- Net Profit: 205.364%
- Compounding Annual Return: 24.985%
- Drawdown: 21.500%
- Sharpe Ratio: 1.431
- Alpha: 0.132

#### Credit is where credit due
- https://www.ireallytrade.com/newsletters/VIXFix.pdf
