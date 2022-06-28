from datetime import datetime
from server.database import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import DateTime

class SATJobConfig:
  id = "ID"
  unit_prop_vals  = "Unit Propagations"
  decision_vars   = "Derivations of Decision Variables"
  time            = "Time of Execution"
  algorithm       = "Algorithm"
  benchmark       = "Benchmark"
  log_file        = "Log File"
  date            = "Date of Run"


class SATJob(Base):
  __tablename__ = "sat_jobs"
  id              = Column(SATJobConfig.id, Integer, primary_key=True)
  unit_prop_vals  = Column(SATJobConfig.unit_prop_vals, Float)
  decision_vars   = Column(SATJobConfig.decision_vars, Float)
  time            = Column(SATJobConfig.time, Float)
  algorithm       = Column(SATJobConfig.algorithm, String(32))
  benchmark       = Column(SATJobConfig.benchmark, String(32))
  log_file        = Column(SATJobConfig.log_file, String(128))
  date            = Column(SATJobConfig.date, DateTime, default=datetime.utcnow)
