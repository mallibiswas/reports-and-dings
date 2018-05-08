# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 13:06:47 2018

@author: mallinath.biswas
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 14:09:30 2018

@author: mallinath.biswas
"""

#!/anaconda3/bin/python3.5

# Note: Run using Python 3.x
#

import pandas as pd
import numpy as np
from functools import reduce
from modules import initialize
import logging
import logging.config

module_logger = logging.getLogger("mainApp.processsing")
globalVars = initialize.readConfigFile()


class dataProcessing():
    
    def __init__ (self, df_):
        self.df_ = df_
    
    def applyDataCleanup (self):
    
        # configure logger
        logger = logging.getLogger("mainApp.processing.add")
    
        # Eliminate campaings below the test or control store count threshold DIG 164
        self.df = self.df_[(self.df_['TestStoreCount'] >= float(globalVars.MINTESTSTORECOUNT)) & (self.df_['ControlStoreCount'] >= float(globalVars.MINCONTROLSTORECOUNT))].copy()
    
        self.df.loc[self.df['ReportedFeaturedSalesPValue'] <= 0,'ReportedFeaturedSalesPValue'] = None
        self.df.loc[self.df['ReportedHaloSalesPValue'] <= 0,'ReportedHaloSalesPValue'] = None
    
        self.df.loc[self.df['ReportedFeaturedSalesLiftMultiplier'] <= 1, 'ReportedFeaturedSalesLiftMultiplier'] = None
        self.df.loc[self.df['ReportedHaloSalesLiftMultiplier'] <= 1, 'ReportedHaloSalesLiftMultiplier'] = None
        
        self.df.loc[self.df['ReportedFeaturedIncrementalSales'] <= 0, 'ReportedFeaturedIncrementalSales'] = None
        self.df.loc[self.df['ReportedHaloIncrementalSales'] <= 0, 'ReportedHaloIncrementalSales'] = None
        
        self.df.loc[(self.df['EstFeaturedCampaignTestSales'] <= 0) | (self.df['EstFeaturedCampaignTestSales'] >= 1e10), 'EstFeaturedCampaignTestSales'] = None
        self.df.loc[(self.df['EstHaloCampaignTestSales'] <= 0) | (self.df['EstHaloCampaignTestSales'] >= 1e10), 'EstHaloCampaignTestSales'] = None
    
        # DIG 164: if Featured Lift or P-Vale is null then set lift and P-Value, Confidence to null and vice versa
        self.df.loc[self.df['ReportedFeaturedSalesLiftMultiplier'].isnull() | self.df['ReportedFeaturedSalesPValue'].isnull() , ['ReportedFeaturedSalesLiftMultiplier','ReportedFeaturedSalesPValue']] = None
        # DIG 164: if Halo Lift or P-Vale is null then set lift and P-Value, Confidence to null and vice versa
        self.df.loc[self.df['ReportedHaloSalesLiftMultiplier'].isnull() | self.df['ReportedHaloSalesPValue'].isnull(), ['ReportedHaloSalesLiftMultiplier','ReportedHaloSalesPValue']] = None
        
        # Modify dates fron object to datetime
        self.df['BeginDate'] = pd.to_datetime(self.df['BeginDate']).dt.date
        self.df['EndDate'] = pd.to_datetime(self.df['EndDate']).dt.date
      
            
        logger.debug("Executed processing.applyDataCleanup:{}".format(self.df.head())) 
            
        return self.df

class deriveMetrics ():
    
    def __init__ (self, df):
        self.df = df
    
    def calculations (self):
    
        # configure logger
        logger = logging.getLogger("mainApp.processing.add")
        
        # Estimated Impressions Per Store Per Week
        self.df['EstImpPerStorePerWeek'] = np.where((self.df['EndDate'] > self.df['BeginDate']) & (self.df['TestStoreCount'] > 0), \
        self.df['EstImpressions']/self.df['TestStoreCount']/self.df['CampaignWeeks'], None).astype(float)     
        
        # derive "lift" variables form "lift multipliers"
        self.df['ReportedFeaturedSalesLift'] = self.df['ReportedFeaturedSalesLiftMultiplier']-1
        self.df['ReportedHaloSalesLift'] = self.df['ReportedHaloSalesLiftMultiplier']-1
    
        self.df['ReportedFeaturedSalesConfidence']= 1 - self.df['ReportedFeaturedSalesPValue']
        self.df['ReportedHaloSalesConfidence'] = 1 - self.df['ReportedHaloSalesPValue']
    
        logger.debug("Executed processing.applyDataCleanup:{}".format(self.df.head())) 
        
        return self.df


class reports():

    def __init__ (self, df):
        self.df = df

    @staticmethod    
    def getColumnLabelDict (labelDict, positionKey):
    
        # configure logger
        logger = logging.getLogger("mainApp.processing.add")
        
        columnNames = []
        columnLabels = []
        columnPositions = []
        sortedColumns = []
        
        for d in labelDict: 
            columnNames.append(d["columnName"])
            columnLabels.append(d["columnLabel"])
            columnPositions.append(int(d[positionKey]))
    
        outDict = dict(zip(columnNames, columnLabels)) # create column:label map    
        positionDict = dict(zip(columnNames, columnPositions)) # create column:position map    
    
        # sort the position dict by columnPosition #
        for w in sorted(positionDict, key=positionDict.get, reverse=False):
            sortedColumns.append(w)
            
        logger.debug("Executed processing.getColumnLabelDict") 
    
        return outDict, sortedColumns
    
     
    def createCampaignDetailsReport (self):
        
        # configure logger
        logger = logging.getLogger("mainApp.processing.add")
    
        # Default sort = descending on End Date DIG 164
        self.df.sort_values('EndDate', axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last')    
    
        columnNamesDict, sortedColumns = self.getColumnLabelDict (globalVars.DETAILSREPORTCOLUMNFORMATSDICT, positionKey="columnPosition")
        
        _df = self.df[sortedColumns] # subset columns also sort in order of columnPositions
        _df_ = _df.rename(columns=columnNamesDict) # Map columns to report labels
    
        logger.debug("Executed processing.createCampaignDetailsReport:{}".format(_df_.head())) 
        
        return _df_
    
    
    def createCampaignSummaryReport (self):
    
        # configure logger
        logger = logging.getLogger("mainApp.processing.add")
        
        # initialize metrics    
        self.df['FeaturedItem75Conf'] = 0
        self.df['HaloItem75Conf'] = 0
        self.df['NewItemCampaignFlag'] = 0
        self.df['ExistingItemCampaignFlag'] = 0
        self.df['CampaignSales'] = 0
        self.df['CampaignCount'] = 1
        
        # derive metrics
        self.df.loc[(self.df['ReportedFeaturedSalesConfidence'] >= float(globalVars.MINFEATUREDSALESCONFIDENCE)) & (self.df['ReportedFeaturedSalesLift'] > 0), 'FeaturedItem75Conf'] = 1
        self.df.loc[(self.df['ReportedHaloSalesConfidence'] >= float(globalVars.MINHALOSALESCONFIDENCE)) & (self.df['ReportedHaloSalesLift'] > 0), 'HaloItem75Conf'] = 1    
        self.df.loc[self.df['CampaignType'].isin (['New Item','New item','New/NPI']), 'NewItemCampaignFlag'] = 1
        self.df.loc[self.df['CampaignType'].isin (['Existing','Existing Item','Scale','Scale Event']), 'ExistingItemCampaignFlag'] = 1
        self.df['CampaignSales'] = self.df['EstFeaturedCampaignTestSales'].fillna(0) + self.df['EstHaloCampaignTestSales'].fillna(0) 
    
        aggFunc = globalVars.AGGREGATIONFUNCTION # load aggregation function dictionary from configs
        
        aggCols = list(aggFunc.keys()) # extract column names from aggFunc
        
        df0 = self.createCampaignSummaryAggregates (self.df, indexCol='CustomerName', aggCol=aggCols, aggFunc=aggFunc)
    
        # conditional aggregations
        
        # Median FI Sales Lift for campaigns with >=75% Confidence
        featured_lifts = self.createCampaignSummaryAggregates (self.df[self.df.FeaturedItem75Conf == 1], indexCol='CustomerName', aggCol='ReportedFeaturedSalesLift', aggFunc='median')
        
        # Median HI Sales Lift for campaigns with >=75% Confidence
        halo_lifts = self.createCampaignSummaryAggregates (self.df[self.df.HaloItem75Conf == 1], indexCol='CustomerName', aggCol='ReportedHaloSalesLift', aggFunc='median')
        
        # Median Featured Item Sales Rate for existing Campaigns (Campaign vs. Previous 52 Weeks)
        SPRs = self.createCampaignSummaryAggregates (self.df[self.df.ExistingItemCampaignFlag == 1], indexCol='CustomerName', aggCol='AvgFeaturedTestSPR', aggFunc='median')
        
        # Merge all the dataframes
        dfs = [df0, featured_lifts, halo_lifts, SPRs]
        _df = reduce(lambda left,right: pd.merge(left, right, how='left', on='CustomerName'), dfs)    
    
        _df.set_index('CustomerName', inplace=True)
        
        _df.sort_values(by='CampaignCount',ascending=False,inplace=True)
    
        columnNamesDict, sortedColumns = self.getColumnLabelDict (globalVars.SUMMARYREPORTROWFORMATSDICT, positionKey="rowPosition")
        _df = _df[sortedColumns] # subset and order columns as specified in formats dict
        _df_ = _df.rename(columns=columnNamesDict) # Map columns to report labels
    
        logger.debug("Executed processing.createCampaignSummaryReport:{}".format(_df_.head())) 
    
        return _df_.transpose() 
           
    @staticmethod
    def createCampaignSummaryAggregates (df, indexCol, aggCol, aggFunc):
    
        # configure logger
        logger = logging.getLogger("mainApp.processing.add")
        
        # Subset dataframe to only cols needed for aggregation    
        if type(aggCol) is list:
            cols = list(aggCol)
            cols.append(indexCol)
        else:
            cols = [indexCol, aggCol]
        df = df[cols]
        
        agg_df0 = df.groupby(by=indexCol, as_index=False)[aggCol].agg(aggFunc)
        agg_df1 = df.groupby(lambda x: True, as_index=False).agg(aggFunc)    
        agg_df1[indexCol]='ALL'    
    
        logger.debug("Executed processing.createCampaignSummaryAggregates:{}".format(agg_df1.head())) 
        
        return agg_df0.append(agg_df1)    



