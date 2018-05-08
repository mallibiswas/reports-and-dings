Python Version:

Python 3.5, 3.6 

Installation:

For a list/versions of installed python packages for the environment where this code was developed refer to "Installed Packages" file

Structure: 	

1. \CampaignHistory\CampaignHistory.py: Main program
2. \CampaignHistory\logging.conf: Configuration file the python logger
3. \CampaignHistory\outlier.log: log file output from the python logger
3. \CampaignHistory\config.ini: configuration file to store all variables needed for code to run
4. \CampaignHistory\formats.json: json file with output excel formats stores in key-value pairs
5. \CampaignHistory\queries.json: json file stores queries needed to execute on prod DB
6. \CampaignHistory\modules\ contains modules imported by CampaignHistory.py 
7. \CampaignHistory\modules\inputs.py: processes input data
8. \CampaignHistory\modules\initialize.py: decrypts/initializes global variables needed for the program to run
9. \CampaignHistory\modules\processing.py: core logic for creating the history and summary reports
10. \CampaignHistory\modules\outputs.py: processes output data and writes to file(s)

Example Call:
 
> python <main program> <configuration file> <excel formats file>
> python CampaignHistory.py config.ini formats.json

Configuration:

The configuration file is config.ini, the variables that will need to be configured are:

[Connections]

Driver = the default sql server driver listed in odbc manager
Server = the server name
Database = databse name

A trusted connection will be made to the database under the account executing to code

[Directories]

ReportDirectory = Path to the directory where the latest report will be written
ArchiveDirectory = Path to the directory where reports will be archived 

Output:

Output file is written to the the directory configured in config.ini 

The output file is in excel (.xlsx) and is of the format CampaignHistoryReport-YYYYMMDD_HHMISS. it has 3 tabs: CampaignDetails, CampaignSummary and Definitions 

The output directory is cleared of all old reports and then a new report is placed there, also a copy is made in Archive/ subdirectory