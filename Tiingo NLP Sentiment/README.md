# Tiingo NLP Sentiment

This is a simple Alpha Model, Tiingo NLP Sentiment, as an example of how you can use the alternative data for the Alpha Model.In this algorithm, we use Tiingo's News to filter for Technology ETF in the universe.

The Alpha Model takes a collection of the highest volume stocks in technolgy sector, collects words indicating the sentiment, and scores the positive or negative side of the news for each asset. The sentiment score is calculated using VaderSentiment. The sum of the sentiment score is calculated for each security and then used as a proxy for the direction and weight of the insights. We take a long position in the top 10 assets by sentiment ranking. The algorithm emits 10 insights per day.

One of the limitations with this model is that the words used are not exhaustive and more could be added to better categorize positive and negative sentiment. The sample size, accuracy of describing a trend of an asset, and the scoring scale determine the trade signal and algorithm's performance. Generally speaking, the larger the sample size,the more precise the scoring scale is, and the more accurately the signal. If we polish the description words sample pool, the result should reflect this more refined.

## Results
- Backtest Timeframe: 2016-2020
- Net Profit: 183.821%
- Compounding Annual Return: 23.171%
- Drawdown: 18.400%
- Sharpe Ratio: 1.006
- Alpha: 0.088

#### Credit is where credit due
- https://github.com/cjhutto/vaderSentiment
- https://www.youtube.com/watch?v=TPO_AwCSL5w 
