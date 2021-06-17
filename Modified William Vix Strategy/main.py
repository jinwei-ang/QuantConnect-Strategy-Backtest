import numpy as np
from QuantConnect.Data.Custom.CBOE import *

class WellDressedYellowGreenEagle(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016,1,1)  # Set Start Date
        self.SetEndDate(2020,12,31)
        self.SetCash(1000000)  # Set Strategy Cash
        self.cap = 1000000
        
        res = Resolution.Hour
        
        self.STOCKS = [self.AddEquity(ticker, res).Symbol for ticker in ['SPY']]
        self.BONDS = [self.AddEquity(ticker, res).Symbol for ticker in ['TLT']]
        
        self.VIX = self.AddData(CBOE, "VIX").Symbol
        self.UUP = self.AddEquity('UUP', res).Symbol
        self.MKT = self.STOCKS[0]
        self.spy = []
        
        self.VOLA = 22;
        self.BULL = 1;
        self.COUNT = 0;
        self.OUT_DAY = 0;
        self.RET_INITIAL = 5;
        self.LEV = 1.00;
        
        self.Schedule.On(self.DateRules.EveryDay(), self.TimeRules.AfterMarketOpen('SPY', 30), self.daily_check)

        # Set Boilinger Bands
        self.bband = self.BB("VIX", 22, 2, MovingAverageType.Simple, Resolution.Daily)
        # Set WarmUp period
        self.SetWarmUp(30)
        

    def daily_check(self):
        
        vola = self.History([self.MKT], self.VOLA + 1, Resolution.Daily).loc[self.MKT][
                   'close'].pct_change().std() * np.sqrt(252)
        WAIT_DAYS = int(vola * self.RET_INITIAL)
        RET = int((1.0 - vola) * self.RET_INITIAL)
        
        price = self.Securities['VIX'].Price

        ratio = price / self.bband.UpperBand.Current.Value
        
        exit = ratio > 1.0
        
        if exit:
            self.BULL = 0;
            self.OUT_DAY = self.COUNT;
        elif (self.COUNT >= self.OUT_DAY + WAIT_DAYS):
            self.BULL = 1
        self.COUNT += 1
        
        wt_stk = self.LEV if self.BULL else 0;
        wt_bnd = 0 if self.BULL else self.LEV;

        wt = {}

        for sec in self.STOCKS:
            wt[sec] = wt_stk / len(self.STOCKS);

        for sec in self.BONDS:
            wt[sec] = wt_bnd / len(self.BONDS)
        
        for sec, weight in wt.items():
            cond1 = (self.Portfolio[sec].Quantity > 0) and (weight == 0)
            cond2 = (self.Portfolio[sec].Quantity == 0) and (weight > 0)
            if cond1 or cond2:
                self.SetHoldings(sec, weight)
    
        self.Plot("Ratio", "Ratio", ratio)

        self.Plot("BB", "Close", self.Securities['VIX'].Close)
        self.Plot("BB", "UpperBand", self.bband.UpperBand.Current.Value)
        self.Plot("BB", "MiddleBand", self.bband.MiddleBand.Current.Value)
        self.Plot("BB", "LowerBand", self.bband.LowerBand.Current.Value)
        
        # to plot SPY on the same chart as the performance of our algo
        hist = self.History([self.MKT] , 252, Resolution.Daily)['close'].unstack(level=0).dropna()
        self.spy.append(hist[self.MKT].iloc[-1])
        spy_perf = self.spy[-1] / self.spy[0] * self.cap
        self.Plot("Strategy Equity", "SPY", spy_perf)