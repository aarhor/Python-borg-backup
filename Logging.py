import datetime
import os
from enum import Enum


class enum_LogLevel(Enum):
    debug = 0
    info = 1
    warning = 2
    error = 3
    fatal = 4


def Write_Log(STATUS, MESSAGE, LogFile):
    if not os.path.exists(LogFile):
        os.makedirs(os.path.dirname(LogFile), exist_ok=True)

    date_Log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    date_Log = date_Log[:-3]
    logMessage = f"{date_Log}\t{STATUS}\t|  {MESSAGE}"

    with open(LogFile, "a+") as f:
        f.write(f"{logMessage}\n")

    print(logMessage)
    return f"{logMessage}\n"


def LOG_DEBUG(MESSAGE, LogFile, LogLevel):
    if enum_LogLevel.debug.value >= enum_LogLevel[LogLevel.lower()].value:
        return Write_Log("DEBUG", MESSAGE, LogFile)

    return ""


def LOG_INFO(MESSAGE, LogFile, LogLevel):
    if enum_LogLevel.info.value >= enum_LogLevel[LogLevel.lower()].value:
        return Write_Log("INFO", MESSAGE, LogFile)

    return ""


def LOG_WARNING(MESSAGE, LogFile, LogLevel):
    if enum_LogLevel.warning.value >= enum_LogLevel[LogLevel.lower()].value:
        return Write_Log("WARNING", MESSAGE, LogFile)

    return ""


def LOG_ERROR(MESSAGE, LogFile, LogLevel):
    if enum_LogLevel.error.value >= enum_LogLevel[LogLevel.lower()].value:
        return Write_Log("ERROR", MESSAGE, LogFile)

    return ""


def LOG_FATAL(MESSAGE, LogFile, LogLevel):
    if enum_LogLevel.fatal.value >= enum_LogLevel[LogLevel.lower()].value:
        return Write_Log("FATAL", MESSAGE, LogFile)

    return ""
