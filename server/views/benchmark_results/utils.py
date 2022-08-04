import os
import traceback

from logzero import logger
from server import db
from server.config import Config
from server.models.job import SATJob, SATJobConfig, enumerateSATJobConfig

def create_col(
  label,
  labelShort,
  sort_asc=True,
  should_be_displayed=True,
  should_be_categorized=True,
  should_be_plotted=False,
  can_be_pressed=False):
  return {
    "label": label,
    "field": labelShort,
    "sort": "asc" if sort_asc else "desc",
    "categorized": should_be_categorized,
    "displayed": should_be_displayed,
    "plotted": should_be_plotted,
    "can_be_pressed": can_be_pressed,
  }

def create_row(row):
  return {
    SATJobConfig.algorithm.long:       getattr(row, "algorithm"),
    SATJobConfig.benchmark.long:       getattr(row, "benchmark"),
    SATJobConfig.time.long:            getattr(row, "time"),
    SATJobConfig.decision_vars.long:   getattr(row, "decision_vars"),
    SATJobConfig.unit_prop_vals.long:  getattr(row, "unit_prop_vals"),
    SATJobConfig.log_file.long:        getattr(row, "log_file"),
    SATJobConfig.date.long:            getattr(row, "date").strftime("%d/%m/%Y, %H:%M:%S"),
  }

should_be_categorized = {
  SATJobConfig.algorithm.long,
  SATJobConfig.benchmark.long
}

shouldnt_be_displayed = {
  SATJobConfig.id.long
}

should_be_plotted = {
  SATJobConfig.decision_vars.long,
  SATJobConfig.time.long,
  SATJobConfig.unit_prop_vals.long
}

can_be_pressed = {
  SATJobConfig.log_file.long
}

def get_data():
  colDefs = enumerateSATJobConfig()
  columns = []
  for col in colDefs:
    if col.long in shouldnt_be_displayed:
      continue
    columns.append(create_col(
      col.long,
      col.short,
      should_be_categorized=col.long in should_be_categorized,
      should_be_plotted=col.long in should_be_plotted,
      can_be_pressed=col.long in can_be_pressed
    ))
  logger.debug(f"returned column definitions: {columns}")
  rows = []
  for row in SATJob.query.all():
    rows.append(create_row(row))
  return {
    "columns": columns,
    "rows": rows
  }