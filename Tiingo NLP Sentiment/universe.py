from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class UniverseSelectionModel(FundamentalUniverseSelectionModel):
    
    def __init__(self, fine_size=10):

        self.fine_size = fine_size
        self.month = -1
        super().__init__(True)


    def SelectCoarse(self, algorithm, coarse):

        if algorithm.Time.month == self.month:
            return Universe.Unchanged
        coarse_filter =  [x for x in coarse if x.HasFundamentalData and float(x.Price) > 5]
        coarse_sorted = sorted(coarse_filter, key=lambda x: x.DollarVolume, reverse=True) 
        return [ x.Symbol for x in coarse_sorted[:200] ]
        # return [ x.Symbol for x in coarse if x.HasFundamentalData and x.DollarVolume >= 100000000 and x.Price >= 10]
    
        
    def SelectFine(self, algorithm, fine):

        self.month = algorithm.Time.month
        
        news_stocks = [ f for f in fine if (f.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.Technology 
                                    or f.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.ConsumerCyclical 
                                    or f.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.FinancialServices 
                                    or f.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.BasicMaterials)]
        fine_stocks = [ f for f in news_stocks if f.CompanyProfile.MarketCap > 5e8 and f.ValuationRatios.ForwardEarningYield > 0 ]
        sorted_stocks = sorted(fine_stocks, key=lambda x: x.MarketCap, reverse=True)
        return [ x.Symbol for x in sorted_stocks[:self.fine_size] ]