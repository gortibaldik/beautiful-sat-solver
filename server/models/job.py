from datetime import datetime
from satsolver.utils.stats import SATSolverStats
from server.database import Base
from server.models.utils import create_n_commit
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
  conflicts       = Descr("Conflicts", "Cs")
  learned_clauses = Descr("Max Learned Clauses", "MLCs")
  time            = Descr("Time of Execution", "ToE")
  algorithm       = Descr("Algorithm", "Algo")
  benchmark       = Descr("Benchmark", "Bench")
  log_file        = Descr("Log File", "Log")
  date            = Descr("Date of Run", "Date")

  @staticmethod
  def create_row(row):
    row_dict = {}
    for name, descr in enumerateSATJobConfig():
      if name != "date":
        row_dict[descr.long] = getattr(row, name)
        continue
      date = getattr(row, name)
      row_dict[descr.long] = date.strftime("%m/%d/%Y, %H:%M:%S")
    return row_dict


def enumerateSATJobConfig():
  """Generator yields name of the field and its description (short name, long name of the column)"""
  for name in dir(SATJobConfig):
    if name.startswith("__") or name == "create_row":
      continue
    yield name, SATJobConfig.__dict__[name]

class SATJob(Base):
  __tablename__   = "sat_jobs"
  id              = Column(SATJobConfig.id.long, Integer, primary_key=True)
  unit_prop_vals  = Column(SATJobConfig.unit_prop_vals.long, Float)
  unit_checked    = Column(SATJobConfig.unit_checked.long, Float)
  decision_vars   = Column(SATJobConfig.decision_vars.long, Float)
  conflicts       = Column(SATJobConfig.conflicts.long, Float)
  learned_clauses = Column(SATJobConfig.learned_clauses.long, Float)
  time            = Column(SATJobConfig.time.long, Float)
  algorithm       = Column(SATJobConfig.algorithm.long, String(512))
  benchmark       = Column(SATJobConfig.benchmark.long, String(32))
  log_file        = Column(SATJobConfig.log_file.long, String(512))
  date            = Column(SATJobConfig.date.long, DateTime, default=datetime.utcnow)

def create_sat_job(
  *,
  algorithm_name,
  benchmark_name,
  log_file,
  avg_time,
  stats: SATSolverStats
):
  algo_split = algorithm_name.split(";")
  algo_name_to_save = algo_split[0]
  for i in range(1, len(algo_split)):
    parameter, value = algo_split[i].split('=')
    if value in ["false", "true", "None"]:
      if value == "true":
        algo_name_to_save += "_" + parameter
      continue
    algo_name_to_save += f"_{parameter}{value}"
  sat_job = SATJob(
    unit_prop_vals  = stats.unitProps,
    decision_vars   = stats.decVars,
    conflicts       = stats.conflicts,
    learned_clauses = stats.learnedClausesPeak,
    time            = avg_time,
    algorithm       = algo_name_to_save,
    benchmark       = benchmark_name,
    log_file        = log_file,
    unit_checked    = stats.unitPropCheckedClauses
  )
  return sat_job

def create_n_commit_satjob(
  *,
  algorithm_name,
  benchmark_name,
  storage_file,
  avg_time=0,
  stats=None,
):
  if stats is None:
    stats = SATSolverStats()
  create_n_commit(
    create_sat_job,
    algorithm_name=algorithm_name,
    benchmark_name=benchmark_name,
    log_file=storage_file,
    avg_time=avg_time,
    stats=stats
  )


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
  SATJobConfig.learned_clauses.long,
}

can_be_pressed = {
  SATJobConfig.log_file.long
}
