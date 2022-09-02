from logzero import logger
from server.models.job import Descr, SATJob, SATJobConfig, enumerateSATJobConfig

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
  SATJobConfig.unit_prop_vals.long,
  SATJobConfig.unit_checked.long,
  SATJobConfig.conflicts.long,
}

can_be_pressed = {
  SATJobConfig.log_file.long
}

def sortColDefs(colDef: Descr):
  if colDef.long in can_be_pressed:
    return 10_000
  if colDef.long in should_be_plotted:
    return ord(colDef.long[0])
  if colDef.long in should_be_categorized:
    return ord(colDef.long[0]) + 500
  return ord(colDef.long[0]) + 1_000

def get_data():
  columns = []
  colDefs = []
  for _, col in enumerateSATJobConfig():
    if col.long in shouldnt_be_displayed:
      continue
    colDefs.append(col)
  
  for col in sorted(colDefs, key=sortColDefs):
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
    rows.append(SATJobConfig.create_row(row))
  return {
    "columns": columns,
    "rows": rows
  }