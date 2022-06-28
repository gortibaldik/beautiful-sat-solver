import traceback

from logzero import logger
from server.models.job import SATJob, SATJobConfig

def create_col(
  label,
  sort_asc=True,
  should_be_displayed=True,
  should_be_categorized=True,
  should_be_plotted=False,
  can_be_pressed=False):
  return {
    "label": label,
    "field": label,
    "sort": "asc" if sort_asc else "desc",
    "categorized": should_be_categorized,
    "displayed": should_be_displayed,
    "plotted": should_be_plotted,
    "can_be_pressed": can_be_pressed,
  }

def create_row(row):
  return {
    SATJobConfig.algorithm:       getattr(row, "algorithm"),
    SATJobConfig.benchmark:       getattr(row, "benchmark"),
    SATJobConfig.time:            getattr(row, "time"),
    SATJobConfig.decision_vars:   getattr(row, "decision_vars"),
    SATJobConfig.unit_prop_vals:  getattr(row, "unit_prop_vals"),
    SATJobConfig.log_file:        getattr(row, "log_file"),
    SATJobConfig.date:            getattr(row, "date"),
  }

should_be_categorized = {
  SATJobConfig.algorithm,
  SATJobConfig.benchmark
}

shouldnt_be_displayed = {
  SATJobConfig.id
}

should_be_plotted = {
  SATJobConfig.decision_vars,
  SATJobConfig.time,
  SATJobConfig.unit_prop_vals
}

can_be_pressed = {
  SATJobConfig.log_file
}

def get_data():
  colDefs = SATJob.metadata.tables["sat_jobs"].columns
  columns = []
  for col in colDefs.keys():
    if col in shouldnt_be_displayed:
      continue
    columns.append(create_col(
      col,
      should_be_categorized=col in should_be_categorized,
      should_be_plotted=col in should_be_plotted,
      can_be_pressed=col in can_be_pressed
    ))
  rows = []
  for row in SATJob.query.all():
    rows.append(create_row(row))
  return {
    "columns": columns,
    "rows": rows
  }

def read_log_file(log_file):
  logs = ""
  with open(log_file, 'r') as l:
    for line in l:
      line = line.strip()
      logs += f"{line}</br>"
  
  return logs

def get_log_file_content(log_file_name):
  try:
    return read_log_file(log_file_name)
  except:
    logger.warning(traceback.format_exc())
