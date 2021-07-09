class WellDressedSkyBlueSardine(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 1, 1)
        self.SetEndDate(2020, 12, 31)
        self.SetCash(100000)

        self.AddEquity('SPY')
        
        self.AddUniverse(self.CoarseFilter, self.FineFilter)
        self.UniverseSettings.Resolution = Resolution.Daily
        
        self.Data = {}
        
        self.SetWarmup(1, Resolution.Daily)
        
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Monday, DayOfWeek.Friday), \
                self.TimeRules.At(12, 0), \
                self.Rebalancing)
                         
    def CoarseFilter(self, coarse):
        sortedByDollarVolume = sorted(coarse, key=lambda x: x.DollarVolume, reverse=True)
        return [x.Symbol for x in sortedByDollarVolume if x.Price > 10
                                                and x.HasFundamentalData][:1000]

    def FineFilter(self, fine):
        sortedMktCap = sorted(fine, key=lambda x: x.MarketCap, reverse=True)
        return  [x.Symbol for x in sortedMktCap if x.MarketCap > 2e9][:50]

    def OnSecuritiesChanged(self, changes):
        for x in changes.RemovedSecurities:
            self.Liquidate()
            if x.Symbol in self.Data:
                del self.Data[x.Symbol]
        
        for x in changes.AddedSecurities:
            self.Data[x.Symbol] = SymbolData(self, x.Symbol)

    def OnData(self, data):
        pass
        
    def Rebalancing(self):
        
        SCTR = {}
        
        for symboldata in self.Data.values():
            if symboldata.IsReady():
                SCTR[symboldata.symbol] = symboldata.SCTR()
                

            self.SCTRuniverse = [pair[0] for pair in sorted(SCTR.items(), key=lambda kv: kv[1], reverse=True)[:int(len(SCTR)*0.10)]]
            
            for symbol in self.SCTRuniverse:
                if (not self.Securities[symbol].Invested):
                    self.SetHoldings(symbol, 1/len(self.SCTRuniverse))
                if (self.Securities[symbol].Invested):
                    [self.Liquidate(symbol) for symbol in self.Portfolio.Keys if symbol not in self.SCTRuniverse]
        
class SymbolData:
    
    def __init__(self, algo, symbol):
        
        self.symbol = symbol
        
        self.EMA200 = algo.EMA(symbol, 200, Resolution.Daily)
        self.EMA50 = algo.EMA(symbol, 50, Resolution.Daily)
        self.ROC125 = algo.ROC(symbol, 125, Resolution.Daily)
        self.ROC20 = algo.ROC(symbol, 20, Resolution.Daily)
        self.PPO = algo.PPO(symbol, 12, 26, MovingAverageType.Exponential, Resolution.Daily)
        self.RSI14 = algo.RSI(symbol, 14, MovingAverageType.Simple, Resolution.Daily)
        
        self.PPOWindow = RollingWindow[float](3)
        
        history = algo.History(symbol, 200, Resolution.Daily)
        for index, bar in history.loc[symbol].iterrows():
            self.EMA200.Update(index, bar.close)
            self.EMA50.Update(index, bar.close)
            self.ROC125.Update(index, bar.close)
            self.ROC20.Update(index, bar.close)
            self.PPO.Update(index, bar.close)
            self.RSI14.Update(index, bar.close)
            
            self.PPOWindow.Add(self.PPO.Current.Value)
        
    def SCTR(self):
        return self.EMA200.Current.Value*0.3 + self.EMA50.Current.Value*0.15 + self.ROC125.Current.Value*0.3 + self.ROC20.Current.Value*0.15 \
                + (self.PPOWindow[0] - self.PPOWindow[2])/(3*self.PPOWindow[2]) *0.05 + self.RSI14.Current.Value*0.05
        
    def IsReady(self):
        return self.EMA200.IsReady and self.EMA50.IsReady \
                    and self.ROC125.IsReady and self.ROC20.IsReady\
                    and self.PPO.IsReady and self.RSI14.IsReady
        