import numpy as np
import pandas as pd
from scipy.optimize import minimize
import statsmodels.formula.api as sm

class mean_variance(QCAlgorithm):
    def __init__(self):
        self.symbols = ["SPY","TLT","GLD"]
        self.num = 21*12
        self.reb_feq = 21
        self.count = 0
        
    
    def get_history(self,symbol):
        prices = []
        dates = []
        for i in self.history:
            bar = i[symbol]
            prices.append(np.log(float(bar.Close)))
            dates.append(bar.EndTime)
        symbol.df = pd.DataFrame({'log_price':prices},index = dates)
        symbol.df['log_return'] = symbol.df['log_price'].diff()
        symbol.df = symbol.df.dropna()

    def regression(self):
        for i in self.symbols:
            df = pd.DataFrame({'%s'%str(i):i.df['log_return'], 'SPY':self.spy.df['log_return']})
            i.model = sm.ols(formula = '%s ~ SPY'%str(i), data = df).fit()
            i.intercept = i.model.params[0]
            i.beta = i.model.params[1]
            i.one_month = sum(i.df['log_return'].tail(21))
            


    def Initialize(self):
        self.SetStartDate(2016,1,1)
        self.SetEndDate(2020,12,31)
        self.SetCash(100000)
        
        self.UniverseSettings.Leverage = 1
        
        for i in range(len(self.symbols)):
            equity = self.AddEquity(self.symbols[i],Resolution.Daily).Symbol
            self.symbols[i] = equity
        
        self.history = self.History(self.num, Resolution.Daily)
        for i in self.symbols:
            self.get_history(i)
            i.leng = i.df.shape[0]
            i.mean = np.mean(i.df['log_return'])
            i.std = np.std(i.df['log_return'])
            i.price_list = []
            i.dates_list = []
            
        self.spy = self.symbols[0]
        
        self.regression()


    def OnData(self,data):
        if self.count == 0:

            for i in self.symbols:
                i.alpha = i.one_month - i.intercept - i.beta*self.spy.one_month
            
            
            self.long_list = [x for x in self.symbols]
            #portfolio optimization#
            self.ticker_list = [str(x) for x in self.long_list]
            self.mean_list = [x.mean for x in self.long_list]
            self.cov_matrix = np.cov([x.df['log_return'] for x in self.long_list])
            self.port = optimizer(self.ticker_list,self.mean_list,self.cov_matrix)
            self.port.optimize()
            self.Log(str(self.port.opt_df))
            self.Log(str([str(x) for x in self.long_list]))
            # self.Log(str([str(x) for x in self.short_list]))
            for i in self.long_list:
                self.SetHoldings(i,self.port.opt_df.ix[str(i)])
            # for i in self.short_list:
            #     self.SetHoldings(i,-1/len(self.short_list))

            self.count += 1
            return
        
        if self.count < self.reb_feq:
            for i in self.symbols:
                try:
                    i.price_list.append(np.log(float(data[i].Close)))
                    i.dates_list.append(data[i].EndTime)
                except:
                    self.Log(str(i))
                
            self.count += 1
            return
                
        if self.count == self.reb_feq:
            for i in self.symbols:
                try:
                    i.price_list.append(np.log(float(data[i].Close)))
                    i.dates_list.append(data[i].EndTime)
                    df = pd.DataFrame({'log_price':i.price_list},index = i.dates_list)
                    df = df.diff().dropna()
                    df = pd.concat([i.df,df]).tail(self.num)
                except:
                    pass
            
            self.regression()
            self.Liquidate()
            self.count = 0
            return
            
            
            
class optimizer(object):
    def __init__(self,ticker_list, mean_list,cov_matrix):
        self.tickers = ticker_list
        self.mean_list = mean_list
        self.cov_matrix = cov_matrix
        
    def optimize(self):
        leng = len(self.tickers)
        def target(x, sigma, mean):
            sr_inv = (np.sqrt(np.dot(np.dot(x.T,sigma),x)*252))/((x.dot(mean))*252)
            return sr_inv
        
        x = np.ones(leng)/leng
        mean = self.mean_list
        sigma = self.cov_matrix
        c = ({'type':'eq','fun':lambda x: sum(x) - 1},
             {'type':'ineq','fun':lambda x: 2 - sum([abs(i) for i in x])})
        bounds = [(-1,1) for i in range(leng)]
        res = minimize(target, x, args = (sigma,mean),method = 'SLSQP',constraints = c,bounds = bounds)
        self.opt_weight = res.x
        self.exp_return = np.dot(self.mean_list,res.x)*252
        self.std = np.sqrt(np.dot(np.dot(res.x.T,sigma),res.x)*252)
        self.opt_df = pd.DataFrame({'weight':res.x},index = self.tickers)
        self.opt_df.index = self.opt_df.index.map(str)
        
    def update(self,ticker_list, mean_list,cov_matrix):
        self.tickers = ticker_list
        self.mean_list = mean_list
        self.cov_matrix = cov_matrix
        self.optimize()