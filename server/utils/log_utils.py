import os
import traceback

from logzero import logger
from server import db
from server.config import Config
from server.models.job import SATJob

def is_correct_log_file(log_file):
  log_dir = Config.SATSMT_RESULT_LOGS
  filename = os.path.basename(log_file)

  return os.path.exists(os.path.join(log_dir, filename))

def is_correct_redis_log_file(log_file):
  log_dir = Config.SATSOLVER_REDIS_LOGS
  filename = os.path.basename(log_file)

  return os.path.exists(os.path.join(log_dir, filename))

def read_log_file(log_file, redis_log_file=False):
  logs = "<code>"
  if (not redis_log_file and not is_correct_log_file(log_file)) or \
    (redis_log_file and not is_correct_redis_log_file(log_file)):
    logs = f"<strong>Incorrect filename returned ({log_file})</strong></br>"
  else:
    with open(log_file, 'r') as l:
      for line in l:
        line = line.strip()
        logs += f"{line}</br>"
  
  logs += " </code>"

  return logs

def get_log_file_content(log_file_name, redis_log_file=False):
  try:
    return read_log_file(log_file_name, redis_log_file=redis_log_file)
  except:
    logger.warning(traceback.format_exc())

def remove_log_file(log_file):
  at_least_one = False
  if not is_correct_log_file(log_file):
    logger.warning(f"incorrect log file: {log_file}")
    return
  for row in SATJob.query.filter_by(log_file=log_file):
    at_least_one = True
    db.session.delete(row)
  db.session.commit()
  if at_least_one and os.path.isfile(log_file):
    os.remove(log_file)
