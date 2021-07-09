class CasualFluorescentYellowFly(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 1, 1)  # Start Date
        self.SetEndDate(2020, 12, 31)  # End Date
        self.SetCash(100000) 
        self.res = Resolution.Daily
        self.ticker = self.AddEquity("QQQ", self.res)
        self.KrollQ = Kroll(self, self.ticker.Symbol)
        
        self.AddUniverse(self.CoarseFilter, self.FineFilter)
        self.UniverseSettings.Resolution = Resolution.Daily
        self.UniverseSettings.SetDataNormalizationMode = DataNormalizationMode.SplitAdjusted
        
        self.Data = {}
        
        self.SetWarmup(21, self.res)

    def CoarseFilter(self, coarse):
        sortedByDollarVolume = sorted(coarse, key=lambda x: x.DollarVolume, reverse=True)
        return [x.Symbol for x in sortedByDollarVolume if x.Price > 10
                                                and x.HasFundamentalData][:30]
                                                
    def FineFilter(self, fine):
        sortedByMktCap = sorted(fine, key=lambda x: x.MarketCap, reverse=True)
        universe =  [x.Symbol for x in sortedByMktCap if x.MarketCap > 2e9][:10]
        return universe

    def OnSecuritiesChanged(self, changes):

        for x in changes.RemovedSecurities:
            self.Liquidate(x.Symbol)
            if x.Symbol in self.Data:
                del self.Data[x.Symbol]
        
        for x in changes.AddedSecurities:
            self.Data[x.Symbol] = Kroll(self, x.Symbol)

    def OnData(self, data):
        
        if self.IsWarmingUp: return

        if self.CurrentSlice.Bars.ContainsKey(self.ticker.Symbol): 
            if self.KrollQ.IsReady:
                self.Plot("Chart", "KrollDown", self.KrollQ.ValueDown)
                self.Plot("Chart", "KrollUp", self.KrollQ.ValueUp)
                self.Plot("Chart", "QQQ", data[self.ticker.Symbol].Close)
                
        for symboldata in self.Data.values():
            symbol = symboldata.symbol
            if not data.ContainsKey(symbol): continue
            
            KUp = symboldata.getKrollUp()
            KDn = symboldata.getKrollDn()
            oso = symboldata.get_rsi()
            atr = symboldata.get_atr()
            
            if KUp == 0: return
                        
            symbolClose = float(self.Securities[symbol].Close)
            
            self.buyquantity =  round((0.2*self.Portfolio.TotalPortfolioValue)/
                                (atr*symbolClose))
                                
            if (not self.Portfolio.Invested):
                if symbolClose > KUp:
                    self.MarketOrder(symbol, self.buyquantity*2, False, "Start Position")
                    
            if  (self.Portfolio[symbol].Invested and (self.Portfolio.Cash >0.20*self.Portfolio.TotalPortfolioValue)):
                if  (KUp/KDn < 1.05) and \
                    (symbolClose > KDn) and \
                    (oso < 30):
                    self.MarketOrder(symbol, self.buyquantity, False, "Add to position")  
                    
            if  (self.Portfolio[symbol].Invested): 
                if KDn > symbolClose:
                    self.Liquidate(symbol, "Exit Signal")
            
class Kroll:
    
    def __init__(self, algo, symbol):
        
        self.symbol = symbol
        self.res = Resolution.Daily
        self.p = 10
        self.period = 20
        self.multiplier = 1
        
        self.atr = algo.ATR(symbol, self.p, self.res)
        self.high = algo.MAX(self.symbol, self.period, self.res, Field.High)
        self.low =  algo.MIN(self.symbol, self.period, self.res, Field.Low)
        self.rsi = algo.RSI(symbol, self.p, self.res)
        
        self.ValueDown = 0
        self.ValueUp = 0
        
        self.Bars = RollingWindow[IBaseDataBar](self.period)
        self.atrWindow = RollingWindow[float](self.p)
        self.highWindow = RollingWindow[float](self.period)
        self.lowWindow = RollingWindow[float](self.period)
        self.atrDown1 = RollingWindow[float](self.period)
        self.atrUp1 = RollingWindow[float](self.period)
        self.atrDown = RollingWindow[float](self.period)
        self.atrUp = RollingWindow[float](self.period)
        
        history = algo.History(symbol, self.period + 10, self.res)
        for bar in history.iloc[-10:].itertuples():
            tradeBar = TradeBar(bar.Index[1], bar.Index[0], bar.open, bar.high, bar.low, bar.close, bar.volume, timedelta(1))
            self.atr.Update(tradeBar)
            
        for index, bar in history.loc[symbol].iterrows():
            self.high.Update(index, bar.close)
            self.low.Update(index, bar.close)
            self.rsi.Update(index, bar.close)
            
        algo.Consolidate(self.symbol, self.res, self.OnStart)
    
    def OnStart(self, bar):
        self.Bars.Add(bar)
        
        if not self.atr.IsReady:
            self.IsReady = False
            return
        else: 
            self.atrWindow.Add(self.atr.Current.Value)
            self.highWindow.Add(self.high.Current.Value)
            self.lowWindow.Add(self.low.Current.Value)
            
        if not self.Bars.IsReady or not self.atrWindow.IsReady:
            self.IsReady = False
            return
        else: 
            self.calculateAtrUpAtrDown()
            
        if not self.atrUp.IsReady or not self.atrDown.IsReady:
            self.IsReady = False
            return
        else:
            self.calculateKroll()

        self.IsReady = True
    
    def IsReady(self):
        return self.atr.IsReady and self.atrDown.IsReady and self.atrUp.IsReady \
        and self.Bars.IsReady 
        
    def calculateAtrUpAtrDown(self):
        atrDown1 = self.lowWindow[0]  +  self.multiplier * self.atrWindow[0]
        self.atrDown1.Add(atrDown1)
        atrDown = min(self.atrDown1)
        self.atrDown.Add(atrDown)
        
        atrUp1 = self.highWindow[0] -  self.multiplier * self.atrWindow[0]
        self.atrUp1.Add(atrUp1)
        atrUp = max(self.atrDown1)
        self.atrUp.Add(atrUp)
        
    def calculateKroll(self):
        self.ValueUp = self.atrUp[0]
        self.ValueDown = self.atrDown[0]
        
    def getKrollUp(self):
        return self.ValueUp
        
    def getKrollDn(self):
        return self.ValueDown
        
    def get_rsi(self):
        return self.rsi.Current.Value
        
    def get_atr(self):
        return self.atr.Current.Value