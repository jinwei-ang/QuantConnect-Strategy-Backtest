from QuantConnect.Data.Custom.Tiingo import *
import nltk
from vaderSentiment import SentimentIntensityAnalyzer, pairwise
from datetime import datetime, timedelta
import numpy as np

from universe import UniverseSelectionModel

class CompetitionExampleAlgorithm(QCAlgorithm):

    def Initialize(self):
        
        self.SetStartDate(2016, 1, 1) 
        self.SetEndDate(2020, 12, 31)
        self.SetCash(100000)
        
        self.SetBenchmark("SPY")
        
        ## Set Universe Selection Model
        self.SetUniverseSelection(UniverseSelectionModel())
        self.UniverseSettings.Resolution = Resolution.Daily
        
        # download the data 
        self.vaderData = self.Download("https://www.dropbox.com/s/q5udnl4ou35o78f/vader_lexicon.txt?dl=1")

        ## Set Alpha Model
        self.SetAlpha(NewsSentimentAlphaModel(self.vaderData))

        ## Set Portfolio Construction Model
        self.SetPortfolioConstruction(InsightWeightingPortfolioConstructionModel())
        self.Settings.RebalancePortfolioOnInsightChanges = True;
        self.Settings.RebalancePortfolioOnSecurityChanges = True;

        ## Set Execution Model
        self.SetExecution(VolumeWeightedAveragePriceExecutionModel())

        ## Set Risk Management Model
        self.SetRiskManagement(NullRiskManagementModel())

class NewsSentimentAlphaModel:
    
    def __init__(self, vaderData):
        self.day = -1
        self.custom = []
        self.vaderData = vaderData
        
    
    def Update(self, algorithm, data):
        insights = []
        
        # Run the model daily
        if algorithm.Time.day == self.day:
            return insights
            
        self.day = algorithm.Time.day
        
        
        weights = {}
        
        # Fetch the wordSentiment data for the active securities and trade on any
        for security in self.custom:
            
            if not data.ContainsKey(security):
                continue
                
            news = data[security]
            
            #use the Vader Sentiment Package  
            sid = SentimentIntensityAnalyzer(lexicon_file=self.vaderData)
            
            #sid = SentimentAnalyzer()
            sentiment = sid.polarity_scores(news.Description.lower())
            if sentiment["compound"] > 0:
                weights[security.Underlying] = sentiment["compound"]
        
        # Sort securities by sentiment ranking, 
        count = min(10, len(weights)) 
        if count == 0:
            return insights
            
        # Order the sentiment by value and select the top 10
        sortedbyValue = sorted(weights.items(), key = lambda x:x[1], reverse=True)
        selected = {kv[0]:kv[1] for kv in sortedbyValue[:count]}
        
        # Populate the list of insights with the selected data where the sentiment sign is the direction and its value is the weight
        closeTimeLocal = Expiry.EndOfDay(algorithm.Time)
        for symbol, weight in selected.items():
            if weight < 0:
                direction = InsightDirection.Down
            elif weight == 0:
                direction = InsightDirection.Flat
            else:
                direction = InsightDirection.Up
            
            insights.append(Insight.Price(symbol, closeTimeLocal, direction, None, None, None, abs(weight)))
            
        return insights
        
        
    def OnSecuritiesChanged(self, algorithm, changes):
        
        if changes is None: return
    
        for security in changes.AddedSecurities:
            # Tiingo's News is for US Equities
            if security.Type == SecurityType.Equity:
                self.custom.append(algorithm.AddData(TiingoNews, security.Symbol).Symbol)
                
        for security in changes.RemovedSecurities:
            if security.Type == SecurityType.Equity:
                algorithm.RemoveSecurity(security.Symbol)