# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 12:30:46 2018

@author: mallinath.biswas
"""

import json
import datetime
import sys
import configparser
import logging

module_logger = logging.getLogger("mainApp.initialize")

class readConfigFile():
    
    """
        This class reads inputs from the command line and processes the configuration files to setup global variables for the rest of the code
    """    
    
    def __init__(self):

        # configure logger
        logger = logging.getLogger("mainApp.initialize.add")
        
        if len(sys.argv) < 3:
            logger.error ("Invalid Arguments")
            logger.error ("usage: python campaignhistory.py config.ini formats.json")
            sys.exit()
            
        self.configFile = sys.argv[1] 
        self.formatsFile = sys.argv[2]
        
        self.CURRENT_DATETIME = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                        
        self.configs = configparser.ConfigParser()
        self.configs.read(self.configFile)
    
        self.QUERYFILE = self.configs['Files']['queryFile']
    
        driver_ = self.configs['Connections']['Driver']
        server_ = self.configs['Connections']['Server']
        database_ = self.configs['Connections']['Database']
        
        self.DBCONNECTSTR = "Driver={driver};Server={server};Database={database};UID=;PWD=;Trusted_Connection=yes".format(driver=driver_,server=server_,database=database_)
        
        logger.info("Running on:{}".format(server_)) # print the server to connect to
        
        self.ARCHIVEDIRECTORY = self.configs['Directories']['ArchiveDirectory']
        self.REPORTDIRECTORY = self.configs['Directories']['ReportDirectory']
        self.AGGREGATIONFUNCTION = json.loads(self.configs['Functions']['aggregationFunction'])
    
        self.CAMPAIGNCUTOFF = self.configs['Constants']['campaignCutoff'] # campaignCutoff is in months, e.g. -6
        self.MINTESTSTORECOUNT = self.configs['Constants']['MinTestStoreCount']
        self.MINCONTROLSTORECOUNT = self.configs['Constants']['MinControlStoreCount']
        self.MINFEATUREDSALESCONFIDENCE = self.configs['Constants']['MinFeaturedSalesConfidence']
        self.MINHALOSALESCONFIDENCE = self.configs['Constants']['MinHaloSalesConfidence']
    
        self.DATADICTIONARY = json.loads(self.configs['Data Dictionary']['dataDictionary'])
                    
        with open(self.formatsFile) as ff: 
            self.reportFormats = json.load(ff)
            self.HEADERFORMAT = self.reportFormats['headerFormat']
            self.DETAILSREPORTCOLUMNFORMATSDICT = self.reportFormats['DetailsReportColumnFormatsDict'] # Used to create details report
            self.SUMMARYREPORTROWFORMATSDICT = self.reportFormats['SummaryReportRowFormatsDict'] # Additional columns for summary report
            self.METADATAREPORTCOLUMNFORMATSDICT = self.reportFormats['MetadataReportColumnFormatsDict']
            
    
        return logger.info ("Initialized variables and modules")
    
    
