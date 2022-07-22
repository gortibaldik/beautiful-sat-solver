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
  decision_vars   = Descr("Derivations of Decision Variables", "DDVs")
  time            = Descr("Time of Execution", "ToE")
  algorithm       = Descr("Algorithm", "Algo")
  benchmark       = Descr("Benchmark", "Bench")
  log_file        = Descr("Log File", "Log")
  date            = Descr("Date of Run", "Date")

def enumerateSATJobConfig():
  yield SATJobConfig.id
  yield SATJobConfig.unit_prop_vals
  yield SATJobConfig.decision_vars
  yield SATJobConfig.time
  yield SATJobConfig.algorithm
  yield SATJobConfig.benchmark
  yield SATJobConfig.log_file
  yield SATJobConfig.date

class SATJob(Base):
  __tablename__ = "sat_jobs"
  id              = Column(SATJobConfig.id.long, Integer, primary_key=True)
  unit_prop_vals  = Column(SATJobConfig.unit_prop_vals.long, Float)
  decision_vars   = Column(SATJobConfig.decision_vars.long, Float)
  time            = Column(SATJobConfig.time.long, Float)
  algorithm       = Column(SATJobConfig.algorithm.long, String(32))
  benchmark       = Column(SATJobConfig.benchmark.long, String(32))
  log_file        = Column(SATJobConfig.log_file.long, String(128))
  date            = Column(SATJobConfig.date.long, DateTime, default=datetime.utcnow)
