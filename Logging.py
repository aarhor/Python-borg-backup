from datetime import datetime, timedelta
import os
import time
from enum import Enum


class enum_LogLevel(Enum):
    debug = 0
    info = 1
    warning = 2
    error = 3
    fatal = 4


def LogRotation(json_data, LogPath):
    b = os.path.expanduser(LogPath)
    LogRotation = json_data["General"]["LogRotation"]

    for full in os.listdir(b):
        f = os.path.join(b, full)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(f))
        max_mtime = datetime.now() - timedelta(days=LogRotation)

        if file_mtime < max_mtime:
            os.remove(f)


def Write_Log(STATUS, MESSAGE, LogFile, print_Message):
    if not os.path.exists(LogFile) and LogFile != "":
        os.makedirs(os.path.dirname(LogFile), exist_ok=True)

    date_Log = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    logMessage = f"{date_Log}\t{STATUS}\t|  {MESSAGE}"

    if print_Message:  # print Message = True => Write into LogFile and to console
        try:
            with open(LogFile, "a+") as f:
                f.write(f"{logMessage}\n")
        except Exception as e:
            a = ""

        print(logMessage)
    else:  # print Message = False => return logMessage to write into MailMessage variable
        return f"{logMessage}\n"


def LOG_DEBUG(MESSAGE, LogFile, json_data):
    LogLevel_File = json_data["General"]["Logging"]["LogLevel_File"]
    LogLevel_Mail = json_data["General"]["Logging"]["LogLevel_Mail"]

    # stdout and Filelogging
    if enum_LogLevel.debug.value >= enum_LogLevel[LogLevel_File.lower()].value:
        Write_Log("DEBUG", MESSAGE, LogFile, True)

    # Logging Mail
    if enum_LogLevel.debug.value >= enum_LogLevel[LogLevel_Mail.lower()].value:
        return Write_Log("DEBUG", MESSAGE, LogFile, False)

    return ""


def LOG_INFO(MESSAGE, LogFile, json_data):
    LogLevel_File = json_data["General"]["Logging"]["LogLevel_File"]
    LogLevel_Mail = json_data["General"]["Logging"]["LogLevel_Mail"]

    # stdout and Filelogging
    if enum_LogLevel.info.value >= enum_LogLevel[LogLevel_File.lower()].value:
        Write_Log("INFO", MESSAGE, LogFile, True)

    # Logging Mail
    if enum_LogLevel.info.value >= enum_LogLevel[LogLevel_Mail.lower()].value:
        return Write_Log("INFO", MESSAGE, LogFile, False)

    return ""


def LOG_WARNING(MESSAGE, LogFile, json_data):
    LogLevel_File = json_data["General"]["Logging"]["LogLevel_File"]
    LogLevel_Mail = json_data["General"]["Logging"]["LogLevel_Mail"]

    # stdout and Filelogging
    if enum_LogLevel.warning.value >= enum_LogLevel[LogLevel_File.lower()].value:
        Write_Log("WARNING", MESSAGE, LogFile, True)

    # Logging Mail
    if enum_LogLevel.warning.value >= enum_LogLevel[LogLevel_Mail.lower()].value:
        return Write_Log("WARNING", MESSAGE, LogFile, False)

    return ""


def LOG_ERROR(MESSAGE, LogFile, json_data):
    LogLevel_File = json_data["General"]["Logging"]["LogLevel_File"]
    LogLevel_Mail = json_data["General"]["Logging"]["LogLevel_Mail"]

    # stdout and Filelogging
    if enum_LogLevel.error.value >= enum_LogLevel[LogLevel_File.lower()].value:
        Write_Log("ERROR", MESSAGE, LogFile, True)

    # Logging Mail
    if enum_LogLevel.error.value >= enum_LogLevel[LogLevel_Mail.lower()].value:
        return Write_Log("ERROR", MESSAGE, LogFile, False)

    return ""


def LOG_FATAL(MESSAGE, LogFile, json_data):
    LogLevel_File = json_data["General"]["Logging"]["LogLevel_File"]
    LogLevel_Mail = json_data["General"]["Logging"]["LogLevel_Mail"]

    # stdout and Filelogging
    if enum_LogLevel.fatal.value >= enum_LogLevel[LogLevel_File.lower()].value:
        Write_Log("FATAL", MESSAGE, LogFile, True)

    # Logging Mail
    if enum_LogLevel.fatal.value >= enum_LogLevel[LogLevel_Mail.lower()].value:
        return Write_Log("FATAL", MESSAGE, LogFile, False)

    return ""
