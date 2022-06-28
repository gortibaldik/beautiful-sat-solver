from datetime import datetime
from server.database import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import DateTime

class SATJob(Base):
  __tablename__ = "sat_jobs"
  id              = Column(Integer, primary_key=True)
  unit_prop_vals  = Column(Float)
  decision_vars   = Column(Float)
  time            = Column(Float)
  algorithm       = Column(String(32))
  benchmark       = Column(String(32))
  log_file        = Column(String(128))
  date            = Column(DateTime, default=datetime.utcnow)
