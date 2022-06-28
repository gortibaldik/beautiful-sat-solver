import random

from logzero import logger
from server.models.job import SATJob, SATJobConfig

def create_col(label, sort_asc=True, should_be_displayed=True, should_be_categorized=True, should_be_plotted=False):
  return {
    "label": label,
    "field": label,
    "sort": "asc" if sort_asc else "desc",
    "categorized": should_be_categorized,
    "displayed": should_be_displayed,
    "plotted": should_be_plotted
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

def get_data():
  colDefs = SATJob.metadata.tables["sat_jobs"].columns
  columns = []
  for col in colDefs.keys():
    if col in shouldnt_be_displayed:
      continue
    columns.append(create_col(
      col,
      should_be_categorized=col in should_be_categorized,
      should_be_plotted=col in should_be_plotted
    ))
  rows = []
  for row in SATJob.query.all():
    rows.append(create_row(row))
  return {
    "columns": columns,
    "rows": rows
  }