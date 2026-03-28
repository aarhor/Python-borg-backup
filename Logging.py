import datetime
import os


def Write_Log(STATUS, MESSAGE, LogFile):
    if not os.path.exists(LogFile):
        os.makedirs(os.path.dirname(LogFile), exist_ok=True)

    date_Log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    date_Log = date_Log[:-3]
    logMessage = f"{date_Log}\t{STATUS}\t|  {MESSAGE}"

    with open(LogFile, "a+") as f:
        f.write(f"{logMessage}\n")

    print(logMessage)


def LOG_DEBUG(MESSAGE, LogFile):
    Write_Log("DEBUG", MESSAGE, LogFile)


def LOG_INFO(MESSAGE, LogFile):
    Write_Log("INFO", MESSAGE, LogFile)


def LOG_WARNING(MESSAGE, LogFile):
    Write_Log("WARNING", MESSAGE, LogFile)


def LOG_ERROR(MESSAGE, LogFile):
    Write_Log("ERROR", MESSAGE, LogFile)
