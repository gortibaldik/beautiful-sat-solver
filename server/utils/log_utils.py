import os
import traceback

from logzero import logger
from server import db
from server.config import Config
from server.models.job import SATJob

def is_correct_log_file(log_file):
  log_dir = Config.SATSMT_RESULT_LOGS
  filename = os.path.basename(log_file)

  return os.path.isfile(os.path.join(log_dir, filename))

def is_correct_redis_log_file(log_file):
  log_dir = Config.SATSOLVER_REDIS_LOGS
  filename = os.path.basename(log_file)

  return os.path.exists(os.path.join(log_dir, filename))

def read_log_file(log_file, redis_log_file=False):
  logs = []
  if (not redis_log_file and not is_correct_log_file(log_file)) or \
    (redis_log_file and not is_correct_redis_log_file(log_file)):
    logs = f"<strong>Incorrect filename returned ({log_file})</strong></br>"
  else:
    with open(log_file, 'r') as l:
      for line in l:
        line = line.strip()
        logs.append(line)
  
    if len(logs) > Config.SERVER_LOG_FILE_LINE_LIMIT:
      logs = logs[len(logs) - Config.SERVER_LOG_FILE_LINE_LIMIT : ]
    
    logs = "</br>".join(logs)
    logs = "<code>"  + logs + "</code>"

  return logs

def get_log_file_content(log_file_name, redis_log_file=False):
  try:
    return read_log_file(log_file_name, redis_log_file=redis_log_file)
  except:
    logger.warning(traceback.format_exc())

def remove_log_file(log_file):
  at_least_one = False
  for row in SATJob.query.filter_by(log_file=log_file):
    at_least_one = True
    db.session.delete(row)
  db.session.commit()
  if at_least_one and is_correct_log_file(log_file):
    os.remove(log_file)
  else:
    logger.warning(f"incorrect log file: {log_file}")

def clear_redis_std_logs():
  redis_std_logs_file = os.path.join(
    Config.SATSOLVER_REDIS_LOGS,
    Config.SATSOLVER_REDIS_STD_FILENAME
  )
  if os.path.isfile(redis_std_logs_file):
    with open(redis_std_logs_file, 'w') as f:
      print("", file=f)

def clear_redis_error_logs():
  redis_error_logs_file = os.path.join(
    Config.SATSOLVER_REDIS_LOGS,
    Config.SATSOLVER_REDIS_ERROR_FILENAME
  )
  if os.path.isfile(redis_error_logs_file):
    with open(redis_error_logs_file, 'w') as f:
      print("", file=f)
