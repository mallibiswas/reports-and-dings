# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 14:09:30 2018

@author: mallinath.biswas
"""

#!/anaconda3/bin/python3.5

# Note: Run using Python 3.x
#

import pandas as pd
import time

from modules import initialize
from modules import inputs
from modules import outputs
from modules import processing

import logging
import logging.config
from os import path


def setLogger (configFile, propagate):
    
    # setup logger Based on http://docs.python.org/howto/logging.html#configuring-logging    
    config_file_path = path.join(path.dirname(path.abspath(__file__)), configFile)
    if path.isfile(config_file_path) is False:
        raise Exception("Config file {} not found".format(config_file_path))
    else:
        logging.config.fileConfig(config_file_path) 
    logger = logging.getLogger("mainApp");

    logger.propagate = propagate # turn off upper logger including console logging

    return logger


def trackTime ():    
    
    now = time.strftime("%H:%M:%S", time.localtime(time.time()))
    
    return now, time.clock()


#########################
# Main program
#########################

if __name__ == '__main__':

    # setup logger, propagate=True for printing to terminal 
    logger = setLogger('logging.conf', propagate=False)    
    
    now, startClock = trackTime()
    
    logger.info ("Start execution at {}".format(now))
    
    # initialize global variables
    globalVars = initialize.readConfigFile() # set global variabales

    # Derive History
    hist_df = inputs.readData(globalVars.QUERYFILE, ReportGroup="KF").loadQueryFile()    
    hist_df = processing.dataProcessing(hist_df).applyDataCleanup() # apply KF data cleanup rules
    hist_df = processing.deriveMetrics(hist_df).calculations() # derive any KPIs needed    


    # Create reports   
    details_df = processing.reports(hist_df).createCampaignDetailsReport()    
    summary_df = processing.reports(hist_df).createCampaignSummaryReport()
    metadata_df = pd.DataFrame(globalVars.DATADICTIONARY, columns=['Metric','Definition'])
    
    logger.info("Summaries generated for:{}".format(list(summary_df)))

    # write output report and archive
    outputs.writeReports().excelReports({"Summary":summary_df,"Details":details_df,"Metadata":metadata_df}, fileName="CampaignHistoryReport").writeExcelFile() 
       
    now, endClock = trackTime()    
    
    logger.info ("CampaignHistory Job Completed at {} in {} seconds".format(now, int(round(endClock-startClock))))
