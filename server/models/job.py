from datetime import datetime
from server.database import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import DateTime

class Descr:
  def __init__(self, long, short):
    self.long = long
    self.short = short

class SATJobConfig:
  id              = Descr("ID", "ID")
  unit_prop_vals  = Descr("Unit Propagations", "UPs")
  unit_checked    = Descr("No. Checked UP Clauses", "UPCs")
  decision_vars   = Descr("Derivations of Decision Variables", "DDVs")
  time            = Descr("Time of Execution", "ToE")
  algorithm       = Descr("Algorithm", "Algo")
  benchmark       = Descr("Benchmark", "Bench")
  log_file        = Descr("Log File", "Log")
  date            = Descr("Date of Run", "Date")

  @staticmethod
  def create_row(row):
    row_dict = {}
    for name, descr in enumerateSATJobConfig():
      row_dict[descr.long] = getattr(row, name)
    return row_dict


def enumerateSATJobConfig():
  """Generator yields name of the field and its description (short name, long name of the column)"""
  for name in dir(SATJobConfig):
    if name.startswith("__") or name == "create_row":
      continue
    yield name, SATJobConfig.__dict__[name]

class SATJob(Base):
  __tablename__ = "sat_jobs"
  id              = Column(SATJobConfig.id.long, Integer, primary_key=True)
  unit_prop_vals  = Column(SATJobConfig.unit_prop_vals.long, Float)
  unit_checked    = Column(SATJobConfig.unit_checked.long, Float)
  decision_vars   = Column(SATJobConfig.decision_vars.long, Float)
  time            = Column(SATJobConfig.time.long, Float)
  algorithm       = Column(SATJobConfig.algorithm.long, String(32))
  benchmark       = Column(SATJobConfig.benchmark.long, String(32))
  log_file        = Column(SATJobConfig.log_file.long, String(128))
  date            = Column(SATJobConfig.date.long, DateTime, default=datetime.utcnow)
