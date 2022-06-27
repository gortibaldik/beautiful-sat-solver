from datetime import datetime
from server import db

class SATJob(db.Model):
  id              = db.Column(db.Integer, primary_key=True)
  unit_prop_vals  = db.Column(db.Float)
  decision_vars   = db.Column(db.Float)
  time            = db.Column(db.Float)
  algorithm       = db.Column(db.String(32))
  benchmark       = db.Column(db.String(32))
  log_file        = db.Column(db.String(128))
  date            = db.Column(db.DateTime, default=datetime.utcnow)
