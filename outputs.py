from modules import initialize
import pandas as pd
import os
import logging
import shutil

module_logger = logging.getLogger("mainApp.outputs")
globalVars = initialize.readConfigFile()


class writeReports():
    """
        The write reports class has two subclasses, one to write excel reports, the other to write csv reports
    """
    class csvReports():
        """
            This class is for writing csv reports from a dataframe
            inputs: dataframe, output directory, output filename and index = True/False. The index argument will indicate whether to write the index of the df or not
        """

        def __init__ (self, df, outDir, fileName, index):
            self.df = df
            self.outDir = outDir
            self.fileName = fileName 
            self.index = index
            
        def writeCSV (self):
        
            # configure logger
            logger = logging.getLogger("mainApp.outputs.add")
                
            if os.path.exists(self.outDir):
                self.outPath = os.path.join(self.outDir, self.fileName)    
                self.df.to_csv(self.outPath, index=self.index)            
            else:
                return logger.error ("Couid not create csv file: {}".format(self.outPath))
            
            return logger.info ("created csv file: {}".format(self.fileName))
    
    class excelReports():
        """
            This class is for writing multi tab excel reports from a dataframe, also deletes the old report and moves to archive
            inputs: dictionary of dataframes, each df is written to a sheet
                    output directory is set from the global variable (from config file) 
                    archive directory is set from the global variable (from config file) 
                    output filename: a datetime suffix is added to the output filename 
        """
    
        def __init__ (self, dfs, fileName):
            self.dfs = dfs
            self.outDir = globalVars.REPORTDIRECTORY
            self.archiveDir = globalVars.ARCHIVEDIRECTORY            
            self.fileName = fileName +'_{}.xlsx'.format(globalVars.CURRENT_DATETIME)                       

        
        def writeEXCEL (self, df, reportType, sheetName):
        
            # configure logger
            logger = logging.getLogger("mainApp.outputs.add")
            
            if reportType is "Summary":
                df.reset_index(inplace=True)
                
            # Convert the dataframe to an XlsxWriter Excel object. Note that we turn off
            # the default header and skip one row to allow us to insert a user defined
            # header.
                
            df.to_excel(self.excel_writer, sheet_name=sheetName, startrow=1, header=False, index=False)
            
            # Get the xlsxwriter workbook and worksheet objects.
            workbook  = self.excel_writer.book
            worksheet = self.excel_writer.sheets[sheetName]
            
            header_values = list(df)
            
            # Add some cell formats., these formats are loaded from the formats.json file
            header_format = workbook.add_format({'bold': True,'text_wrap': True,'valign': 'vcenter', 'align': 'center','font_size':12,'fg_color': '#bbe2f7','border': 1})
            text_format = workbook.add_format({'font_name':'Calibri','font_size': '11','valign': 'vcenter','align': 'left','border': 0}) # Pretty text
            text_bold = workbook.add_format({'font_name':'Calibri','font_size': '11','align':'right','bold': True,'text_wrap': True}) # Pretty and bold text
            decimal_format = workbook.add_format({'num_format': '#,##0.00'}) # with decimals
            pct_format = workbook.add_format({'num_format': '0.0%'}) # pct in 0.0% format
            pct2_format = workbook.add_format({'num_format': '0.00%'}) # pct - higher precision 0.00%
            int_format = workbook.add_format({'num_format': '#,##0'}) # integers
            money_format = workbook.add_format({'num_format': '$#,##0'})
            date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})
            
            
            if reportType is "Details":
                
                # Write the column headers with the defined format.
                for col_num, value in enumerate(header_values):
                    worksheet.write(0, col_num, value, header_format) # Details header begins at col:0
                
                for d in globalVars.DETAILSREPORTCOLUMNFORMATSDICT: 
                    # set_column(first_col, last_col, width, cell_format, options)
                    p = int(d["columnPosition"])
                    w = int(d["columnWidth"])
                    f = eval(d["columnFormat"]) # load formats
                    worksheet.set_column(p, p, w, f)  
                        
                # Add autofilter worksheet.autofilter (beginrow, begincol, endrow, endcol)
                worksheet.autofilter(0, 0, df.shape[0], df.shape[1]-1)
                
            elif reportType is "Summary":
                
                header_values.pop(0) # take out the index column name    
                
                # Write the column headers with the defined format.
                for col_num, value in enumerate(header_values):
                    worksheet.write(0, col_num+1, value, header_format) # Summary header begins at col:1
            
                worksheet.set_column(1, df.shape[1], 15)  # set data col sizes
                
                for d in globalVars.SUMMARYREPORTROWFORMATSDICT: 
                    # set_column(first_col, last_col, width, cell_format, options)
                    p = int(d["rowPosition"])
                    h = int(d["rowHeight"])
                    f = eval(d["rowFormat"])
                    worksheet.set_row(p, h, f)      
        
                worksheet.set_column('A:A', 60, text_bold)  # set 1st col format, but cannot overwrite pandas default
        
            elif reportType is "Metadata":
        
                # Write the column headers with the defined format.
                for col_num, value in enumerate(header_values):
                    worksheet.write(0, col_num, value, header_format) # Summary header begins at col:1
        
                for d in globalVars.METADATAREPORTCOLUMNFORMATSDICT: 
                    # set_column(first_col, last_col, width, cell_format, options)
                    p = int(d["columnPosition"])
                    w = int(d["columnWidth"])
                    f = eval(d["columnFormat"])
                    worksheet.set_column(p, p, w, f)  
                
            else:
                raise ValueError ("Error in reportType, has to be Summary or Details")            
                
            return logger.info ("Created {} Report".format(reportType))
    
        @staticmethod
        def isDirExists(dirPath):
            
            if os.path.exists(dirPath):
                return True
            else:
                raise ValueError ("Directory {} does not exist".format(dirPath))    
                
            return
    
    
        def writeExcelFile (self):
        
            # configure logger
            logger = logging.getLogger("mainApp.outputs.add")
        
            if self.isDirExists(self.archiveDir):
                archivePath = os.path.join(self.archiveDir, self.fileName) # Archive with datstamp
            else:
                raise ValueError ("Archive Directory Does Not Exist!")
                
            if self.isDirExists(self.outDir):
                outPath = os.path.join(self.outDir, self.fileName) # write main report with datetimestamp
                # delete existing files from outpath
                for oldReport in os.listdir(self.outDir):
                    file_path = os.path.join(self.outDir, oldReport)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            logger.info("Removing Old report:{}".format(file_path))
                    except Exception:
                        logger.error ("Could not remove: {}, skipping".format(oldReport))
                        pass
            else:
                raise ValueError ("Report Directory Does Not Exist!")
                        
                        
            try:
                
                try:
                    self.excel_writer = pd.ExcelWriter(outPath, engine='xlsxwriter', date_format='mm/dd/yyyy')
                except Exception as e:
                    logger.error ("Error launching ExcelWriter: {}".format(str(e)))
                try:
                    self.writeEXCEL (self.dfs["Details"], reportType="Details", sheetName="CampaignDetails")
                except Exception as e:
                    logger.error ("Error writing Details Report: {}".format(str(e)))
                try:
                    self.writeEXCEL (self.dfs["Summary"], reportType="Summary", sheetName="CampaignSummary")
                except Exception as e:
                    logger.error ("Error writing Summary Report: {}".format(str(e)))
                try:
                    self.writeEXCEL (self.dfs["Metadata"], reportType="Metadata", sheetName="Definitions")            
                except Exception as e:
                    logger.error ("Error writing Metadata Report: {}".format(str(e)))
                    
            except Exception as e:
                raise ValueError ("Error writing output file {}, {}".format(self.outPath, str(e)))
                
            finally:
                self.excel_writer.close()
                self.excel_writer.save()
                shutil.copy(outPath, archivePath) # make a copy of the report to file with datestamps
        
            return logger.info ("written {} to: {}".format(self.fileName,self.outDir))


