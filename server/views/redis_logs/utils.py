import os

from server.config import Config
from server.utils.log_utils import get_log_file_content

def get_data():
  base = "<code><strong>Nothing to show</strong> - message from server</code>"
  logDirname = Config.SATSOLVER_REDIS_LOGS
  errorFilename = os.path.join(logDirname, Config.SATSOLVER_REDIS_ERROR_FILENAME)
  stdFilename = os.path.join(logDirname, Config.SATSOLVER_REDIS_STD_FILENAME)

  errorLogFile = get_log_file_content(errorFilename, redis_log_file=True)
  stdLogFile = get_log_file_content(stdFilename, redis_log_file=True)
  return {
    "errorLogs": errorLogFile,
    "stdLogs": stdLogFile,
    "result": "success",
  }