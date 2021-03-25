from os import environ
from datetime import datetime

#TODO: Add in functionality to archive log after a day
# and create log for new day

def writeToLog(log: str) -> None:
    logFile = environ.get('LOGFILE')

    if logFile:
        f = open(logFile, "a")
        f.write("{}\n".format(log))
        f.close()

def formatLogTimestamp() -> str:
    now = datetime.strftime(datetime.now(), "%m/%d/%Y %H:%M:%S")
    formatted = "[{}]".format(now)
    return formatted

def error(msg: str) -> None:
    logMsg = "{} ERROR - {}".format(formatLogTimestamp(), msg)
    writeToLog(logMsg)

def info(msg: str) -> None:
    logMsg = "{} INFO - {}".format(formatLogTimestamp(), msg)
    writeToLog(logMsg)