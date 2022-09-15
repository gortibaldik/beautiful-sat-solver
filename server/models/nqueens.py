from datetime import datetime
from satsolver.utils.stats import SATSolverStats
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import DateTime
from server.database import Base
from server.models.job import Descr
from server.models.utils import create_n_commit


class SATNQueensConfig:
  id              = Descr("ID", "ID")
  unit_prop_vals  = Descr("Unit Propagations", "UPs")
  unit_checked    = Descr("No. Checked UP Clauses", "UPCs")
  decision_vars   = Descr("Derivations of Decision Variables", "DDVs")
  conflicts       = Descr("Conflicts", "Cs")
  learned_clauses = Descr("Max Learned Clauses", "MLCs")
  time            = Descr("Time of Execution", "ToE")
  algorithm       = Descr("Algorithm", "Algo")
  nqueens         = Descr("Number of Queens", "N")
  log_file        = Descr("Log File", "Log")
  date            = Descr("Date of Run", "Date")

  @staticmethod
  def create_row(row):
    row_dict = {}
    for name, descr in enumerateSATNQueensConfig():
      if name != "date":
        row_dict[descr.long] = getattr(row, name)
        continue
      date = getattr(row, name)
      row_dict[descr.long] = date.strftime("%m/%d/%Y, %H:%M:%S")
    return row_dict

def enumerateSATNQueensConfig():
  """Generator yields name of the field and its description (short name, long name of the column)"""
  for name in dir(SATNQueensConfig):
    if name.startswith("__") or name == "create_row":
      continue
    yield name, SATNQueensConfig.__dict__[name]

class SATNQueens(Base):
  __tablename__   = "sat_nqueens"
  id              = Column(SATNQueensConfig.id.long, Integer, primary_key=True)
  unit_prop_vals  = Column(SATNQueensConfig.unit_prop_vals.long, Float)
  unit_checked    = Column(SATNQueensConfig.unit_checked.long, Float)
  decision_vars   = Column(SATNQueensConfig.decision_vars.long, Float)
  conflicts       = Column(SATNQueensConfig.conflicts.long, Float)
  learned_clauses = Column(SATNQueensConfig.learned_clauses.long, Float)
  time            = Column(SATNQueensConfig.time.long, Float)
  algorithm       = Column(SATNQueensConfig.algorithm.long, String(512))
  nqueens         = Column(SATNQueensConfig.nqueens.long, String(32))
  log_file        = Column(SATNQueensConfig.log_file.long, String(512))
  date            = Column(SATNQueensConfig.date.long, DateTime, default=datetime.utcnow)

def create_nqueens(
  *,
  algorithm,
  N,
  log_file,
  avg_time,
  stats: SATSolverStats
):
  algo_split = algorithm.split(";")
  algo_name_to_save = algo_split[0]
  for i in range(1, len(algo_split)):
    parameter, value = algo_split[i].split('=')
    if value in ["false", "true", "None"]:
      if value == "true":
        algo_name_to_save += "_" + parameter
      continue
    algo_name_to_save += f"_{parameter}{value}"
  sat_job = SATNQueens(
    unit_prop_vals  = stats.unitProps,
    decision_vars   = stats.decVars,
    conflicts       = stats.conflicts,
    learned_clauses = stats.learnedClausesPeak,
    time            = avg_time,
    algorithm       = algo_name_to_save,
    nqueens         = N,
    log_file        = log_file,
    unit_checked    = stats.unitPropCheckedClauses
  )
  return sat_job

def create_n_commit_nqueens(
  *,
  algorithm,
  N,
  storage_file,
  avg_time=0,
  stats=None,
  **kwargs
):
  if stats is None:
    stats = SATSolverStats()
  create_n_commit(
    create_nqueens,
    algorithm=algorithm,
    N=N,
    log_file=storage_file,
    avg_time=avg_time,
    stats=stats
  )


should_be_categorized = {
  SATNQueensConfig.algorithm.long,
  SATNQueensConfig.nqueens.long
}

shouldnt_be_displayed = {
  SATNQueensConfig.id.long
}

should_be_plotted = {
  SATNQueensConfig.decision_vars.long,
  SATNQueensConfig.time.long,
  SATNQueensConfig.unit_prop_vals.long,
  SATNQueensConfig.unit_checked.long,
  SATNQueensConfig.conflicts.long,
  SATNQueensConfig.learned_clauses.long,
}

can_be_pressed = {
  SATNQueensConfig.log_file.long
}
