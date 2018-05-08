import pyodbc
import json
import pandas as pd
import numpy as np
from modules import initialize
import logging

module_logger = logging.getLogger("mainApp.inputs")

globalVars = initialize.readConfigFile()

class readData():
    """
        loops through (and executes) the queries in queryFilename (for a particular reportGroup) and appends all the dataframes to return a single df with all data needed 
    """
    def __init__ (self, queryFilename, ReportGroup):
        self.queryFilename = queryFilename
        self.ReportGroup = ReportGroup

    @staticmethod        
    def processInputDF (operation, base_df, incr_df):
    
        # configure logger
        logger = logging.getLogger("mainApp.inputs.add")
        
        # merge incremental df to the base df or update, depeneding on operation
        incr_df.fillna(np.nan)
        
        if base_df.empty: # should happen the first time the proc is called
            return incr_df
        
        try:
            if operation == "merge" and not base_df.empty:
                df = base_df.merge(incr_df, how='left', suffixes=['_1', '_2'], on=None, left_on=None, right_on=None, left_index=True, right_index=True, sort=True)
                return df
            
            elif operation == "update":
                base_df.update(incr_df)
                return base_df
                
        except Exception as e: # any error here is severe
            logger.error ("Error: merge failed, cannot recognize operation: {}".format(str(e)))
            
        return
    
    def loadQueryFile(self):
    
        # configure logger
        logger = logging.getLogger("mainApp.inputs.add")
    
        # load and read the query file
        with open(self.queryFilename) as f:
           
            queries = json.load(f)[self.ReportGroup]
            queryList = queries["Queries"]        
            indexColumn = queries["Metadata"]["indexColumn"]
            
            base_df = pd.DataFrame(columns=[indexColumn]) # Create null df
            
            
            # loop through all the tablenames
            for j in range(len(queryList)):
    
     
                moduleName = queryList[j]["module"]
                operation = queryList[j]["operation"]
                sourceQuery = queryList[j]["sourceQuery"]
    
                # connect to DB
                try:
                    conn = pyodbc.connect(globalVars.DBCONNECTSTR)            
                except Exception as e:
                    logger.error ("Error in connection {}".format(str(e)))
                    raise
                    
                logger.info ("processing module: {} for Operation: {}".format(moduleName,operation))
                   
                try:
                    incr_df = pd.read_sql(sourceQuery, conn, index_col=indexColumn)
                    base_df = self.processInputDF (operation, base_df = base_df, incr_df = incr_df)
                except Exception as e: # any error here is severe
                    logger.error ("raised exception reading df from sql: {}".format(str(e)))
                    logger.error ("error in source sql:".format(sourceQuery))
                    logger.error (base_df.info())
                finally:    
                    conn.close()
                
        return base_df
