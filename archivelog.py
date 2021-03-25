from os import environ, path
from datetime import datetime
from pathlib import Path
from classes.logger import error, info


if __name__ == "__main__":
    try:
        logFile = environ.get('LOGFILE')
        
        if logFile:
            # construct new file name, get current log directory, construct
            # new file absolute path
            curDate = datetime.strftime(datetime.now(), "%Y-%m-%d")
            newFileName = "app.logger.{}".format(curDate)
            logDir = path.dirname(logFile)
            newFile = path.join(logDir, newFileName)
            exist = path.isfile(newFile)

            if not exist:
                # if the new file doesn't already exist
                # then rename the old one to the new file 
                Path(logFile).rename(newFile)
                info("Logs successfully archived to file {}".format(newFileName))
            else:
                # if the file exists already don't archive
                info("Log file was not archived as {} already exists.".format(newFileName))
        else:
            info("Unable to archive log file. No log file environment variable found.")

    except Exception as e:
        error(str(e))
