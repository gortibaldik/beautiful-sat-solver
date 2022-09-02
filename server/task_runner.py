import traceback
import logzero
import os
import rq
import server.getters

from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from rq.command import send_stop_job_command
from satsolver.utils.check import check_assignment
from satsolver.utils.stats import SATSolverStats
from satsolver.task6 import generate_nqueens_dimacs
from server.database import SessionLocal
from server.config import Config
from server.models.job import SATJob
from server.utils.redis_utils import get_redis_connection
from time import gmtime, strftime

def get_timestamp():
  return strftime("%Y_%m_%d_%H_%M_%S", gmtime())

def ensure_storage_file(algorithm_name, benchmark_name):
  if not algorithm_name or not benchmark_name:
    return None
  storage_folder = Config.SATSMT_RESULT_LOGS
  Path(storage_folder).mkdir(parents=True, exist_ok=True)
  storage_file = os.path.join(storage_folder, f"{algorithm_name}_{benchmark_name}_{get_timestamp()}")
  return storage_file

def ensure_storage_file_custom_run():
  storage_folder = Config.SATSMT_RESULT_LOGS
  Path(storage_folder).mkdir(parents=True, exist_ok=True)
  storage_file = os.path.join(storage_folder, Config.SATSOLVER_CUSTOM_RUN_FILENAME)
  return storage_file

def create_sat_job(
  *,
  algorithm_name,
  benchmark_name,
  log_file,
  avg_time,
  stats: SATSolverStats):
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
  with SessionLocal() as db:
    sat_job = create_sat_job(
      algorithm_name=algorithm_name,
      benchmark_name=benchmark_name,
      log_file=storage_file,
      avg_time=avg_time,
      stats=stats
    )
    db.add(sat_job)
    db.commit()

def retrieve_algorithm(algorithms, algorithm_name):
  algorithm_name, *algorithm_parameters = algorithm_name.split(";")
  parameter_dict = {}
  for p in algorithm_parameters:
    parameter, value = p.split("=")
    if value == "true":
      value = True
    elif value == "false":
      value = False
    elif value == "None":
      value = None
    try:
      value = int(value)
    except:
      try:
        value = float(value)
      except:
        pass
    parameter_dict[parameter] = value

  for _, algo_module in algorithms.items():
    task_info = algo_module.get_info()
    if task_info["name"] == algorithm_name:
      return lambda **kwargs: algo_module.find_model(**kwargs, **parameter_dict)
  return None

def retrieve_benchmark_basedir(benchmark_name):
  all_benchmarks_basedir = Config.SATSMT_BENCHMARK_ROOT
  benchmark_name = os.path.basename(benchmark_name)
  benchmark_basedir = os.path.join(all_benchmarks_basedir, benchmark_name)

  if not os.path.isdir(benchmark_basedir):
    return None
  
  return benchmark_basedir

def retrieve_benchmark_filename(benchmark_name, entry_name):
  benchmark_basedir = retrieve_benchmark_basedir(benchmark_name)
  
  if not benchmark_basedir:
    return None

  benchmark_filename = os.path.join(benchmark_basedir, entry_name)
  if not os.path.isfile(benchmark_filename):
    return None
  return benchmark_filename

def retrieve_benchmark_filenames(benchmark_name):
  benchmark_basedir = retrieve_benchmark_basedir(benchmark_name)
  
  if not benchmark_basedir:
    return None
  
  benchmark_filenames = []
  for f in os.listdir(benchmark_basedir):
    benchmark_filenames.append(os.path.join(benchmark_basedir, f))
  
  return benchmark_filenames

def init_cumulative_stats():
  return {
    "stats": SATSolverStats(),
    "time": 0,
    "total": 0,
  }

def update_cumulative_stats(
  *,
  cumulative_stats,
  result
):
  cumulative_stats["stats"].update(result["stats"])
  cumulative_stats["total"] += 1
  cumulative_stats["time"] += result["time"]

def avg_cumulative_stats(cumulative_stats):
  total = cumulative_stats["total"]
  cumulative_stats["stats"].divide(total)
  cumulative_stats["time"] /= total

def log_level_per_debug_level(debug_level):
  debug, info, warning = False, False, False
  if debug_level == "INFO":
    logzero.logger.info("Selected log level: INFO")
    info = True
  if debug_level == "DEBUG":
    logzero.logger.info("Selected log level: DEBUG")
    debug = True
  if debug_level == "WARNING":
    logzero.logger.info("Selected log level: WARNING")
    warning = True
  
  return debug, info, warning

def benchmark(file, algorithm_name, benchmark_name, debug_level):
  try:
    job = rq.get_current_job()
    job.meta["progress"] = 0
    job.save_meta()
    algorithms = server.getters.get_modules()
    algo_module = retrieve_algorithm(algorithms, algorithm_name)

    if algo_module is None:
      logzero.logger.warning(f"Algorithm with name: {algorithm_name} not found, EXITING!")
      return

    benchmark_filenames = retrieve_benchmark_filenames(benchmark_name)
    if benchmark_filenames is None:
      logzero.logger.warning(f"Benchmark with name: {benchmark_name} not found, EXITING!")
      return

    total_number_of_benchmarks = len(benchmark_filenames)
    cumulative_stats = init_cumulative_stats()
    logzero.logger.warning(f"Algorithm: {algorithm_name}, Benchmark: {benchmark_name}, Log Level: {debug_level}")
    debug, info, warning = log_level_per_debug_level(debug_level)
    check_debug, check_info, check_warning = log_level_per_debug_level(Config.CHECK_LOG_LEVEL)

    for i, filename in enumerate(benchmark_filenames):
      logzero.logger.warning(f"Algorithm: {algorithm_name}, Benchmark: {benchmark_name}, Entry: {filename} Log Level: {debug_level}")
      job.meta['progress'] = i * 100 / total_number_of_benchmarks
      job.save_meta()
      result = algo_module(
        input_file=filename,
        debug=debug,
        warning=warning,
        nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
      )
      check_assignment(
        input_file=filename,
        assignment_source=result["model"],
        debug=check_debug,
        warning=check_warning,
        read_from_file=False,
        is_satisfiable="uuf" not in filename,
        nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
      )
      logzero.loglevel(Config.DEFAULT_LOGLEVEL)
      if result is None:
        break
      update_cumulative_stats(
        cumulative_stats=cumulative_stats,
        result=result
      )
      file.flush()
    avg_cumulative_stats(cumulative_stats)
    logzero.logger.info(f"Stats: {cumulative_stats['stats']}; time: {cumulative_stats['time']}")
  except:
    if filename is not None:
      logzero.logger.warning(f"Filename with error: {filename}")
    logzero.logger.warning(traceback.format_exc())
    return None
  
  return cumulative_stats

def custom_run(
  file,
  algorithm_name,
  benchmark_name,
  entry_name,
  debug_level
):
  benchmark_filename = None
  try:
    algorithms = server.getters.get_modules()
    algo_module = retrieve_algorithm(algorithms, algorithm_name)

    if algo_module is None:
      logzero.logger.warning(f"Algorithm with name: {algorithm_name} not found, EXITING!")
      return

    benchmark_filename = retrieve_benchmark_filename(
      benchmark_name,
      entry_name
    )
    if benchmark_filename is None:
      logzero.logger.warning(f"Benchmark with name: {benchmark_name} not found, EXITING!")
      return

    debug, info, warning = log_level_per_debug_level(debug_level)
    check_debug, check_info, check_warning = log_level_per_debug_level(Config.CHECK_LOG_LEVEL)
    logzero.logger.warning(f"Algorithm: {algorithm_name}, Benchmark: {benchmark_name}, Entry: {entry_name} Log Level: {debug_level}")
    result = algo_module(
      input_file=benchmark_filename,
      debug=debug,
      warning=warning,
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    file.flush()
    check_assignment(
      input_file=benchmark_filename,
      assignment_source=result["model"],
      debug=check_debug,
      warning=check_warning,
      read_from_file=False,
      is_satisfiable="uuf" not in benchmark_filename,
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    logzero.loglevel(Config.DEFAULT_LOGLEVEL)
    file.flush()
  except:
    if benchmark_filename is not None:
      logzero.logger.warning(f"Filename with error: {benchmark_filename}")
    logzero.logger.warning(traceback.format_exc())

def save_model(result):
  if "model" not in result:
    return
  model = result["model"]
  array_to_write = []
  for variable, value in model.items():
    int_var = int(variable)
    if not value:
      int_var *= -1
    array_to_write.append(int_var)
  array_to_write = sorted(array_to_write, key=abs)
  job = rq.get_current_job()
  job.meta["model"] = array_to_write
  job.save_meta()
  

def nqueens(
  file,
  algorithm_name,
  n,
  debug_level
):
  try:
    algorithms = server.getters.get_modules()
    algo_module = retrieve_algorithm(algorithms, algorithm_name)

    if algo_module is None:
      logzero.logger.warning(f"Algorithm with name: {algorithm_name} not found, EXITING!")
      return

    debug, info, warning = log_level_per_debug_level(debug_level)
    check_debug, check_info, check_warning = log_level_per_debug_level(Config.CHECK_LOG_LEVEL)
    logzero.logger.warning(f"Algorithm: {algorithm_name}, nqueens: N = {n} Log Level: {debug_level}")
    benchmark_filename = None
    benchmark_filename = generate_nqueens_dimacs(int(n))
    result = algo_module(
      input_file=benchmark_filename,
      debug=debug,
      warning=warning,
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    file.flush()
    check_assignment(
      input_file=benchmark_filename,
      assignment_source=result["model"],
      debug=check_debug,
      warning=check_warning,
      read_from_file=False,
      is_satisfiable=int(n) != 3,
      nnf_reduce_implications=Config.NNF_REDUCE_IMPLICATIONS
    )
    save_model(result)

    logzero.loglevel(Config.DEFAULT_LOGLEVEL)
    file.flush()
  except:
    if benchmark_filename is not None:
      logzero.logger.warning(f"Filename with error: {benchmark_filename}")
    logzero.logger.warning(traceback.format_exc())

def run_benchmark(
  algorithm_name=None,
  benchmark_name=None,
  debug_level=None,
  finished_meta_key="finished"
):
  job = rq.get_current_job()
  storage_file = ensure_storage_file(algorithm_name, benchmark_name)
  if storage_file is None:
    job.meta['interrupted'] = True
    job.save_meta()
    return
  logzero.logger.info(f"Selected storage file: {storage_file}")
  job.meta[finished_meta_key] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        result = benchmark(f, algorithm_name, benchmark_name, debug_level)
        logzero.logfile(None)
  if result is None:
    result = init_cumulative_stats()
    job.meta['interrupted'] = True
  else:
    job.meta['progress'] = 100.0
    job.meta[finished_meta_key] = True
  job.save_meta()

  try:
    create_n_commit_satjob(
      algorithm_name=algorithm_name,
      benchmark_name=benchmark_name,
      storage_file=storage_file,
      stats=result["stats"],
      avg_time=result["time"]
    )
  except:
    logzero.logfile(storage_file)
    logzero.logger.warning(traceback.format_exc())
    logzero.logfile(None)

  return job

def run_all_benchmarks(algorithm_name=None, debug_level=None):
  job = rq.get_current_job()
  ix = 1
  total = len(list(os.listdir(Config.SATSMT_BENCHMARK_ROOT)))
  job.meta['finished'] = False
  for benchmark_name in os.listdir(Config.SATSMT_BENCHMARK_ROOT):
    job.meta['running_benchmark'] = f"{benchmark_name} ({ix}/{total})"
    job.meta['progress'] = 0
    job.save_meta()
    run_benchmark(
      algorithm_name,
      benchmark_name,
      debug_level,
      finished_meta_key="_fin_"
    )
    ix += 1
  job.meta['finished'] = True
  job.save_meta()

def run_custom_input(
  algorithm_name=None,
  benchmark_name=None,
  entry_name=None,
  debug_level=None
):
  job = rq.get_current_job()
  storage_file = ensure_storage_file_custom_run()
  job.meta['finished'] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        custom_run(
          f,
          algorithm_name,
          benchmark_name,
          entry_name,
          debug_level
        )
        logzero.logfile(None)
  job.meta['finished'] = True
  job.save_meta()

  return job

def run_nqueens(
  algorithm_name=None,
  n=None,
  run_as_benchmark=None,
  timeout=None,
  debug_level=None
):
  job = rq.get_current_job()
  storage_file = ensure_storage_file(algorithm_name, "__nqueens__")
  job.meta['finished'] = False
  job.meta['storage_file'] = storage_file
  job.save_meta()
  with open(storage_file, 'w') as f:
    with redirect_stdout(f):
      with redirect_stderr(f):
        logzero.logfile(storage_file)
        nqueens(
          f,
          algorithm_name,
          n,
          debug_level
        )
        logzero.logfile(None)
  job.meta['finished'] = True
  job.save_meta()

  return job

def task_runner_start(method_name, **kwargs):
  queue = rq.Queue(
    Config.REDIS_WORKER_QUEUE_NAME,
    connection=get_redis_connection(),
    default_timeout=3600
  )
  job = queue.enqueue(method_name, kwargs=kwargs)
  return job


def task_runner_start_algorithm_on_benchmark(algorithm_name, benchmark_name, debug_level):
  return task_runner_start(
    'server.task_runner.run_benchmark',
    algorithm_name=algorithm_name,
    benchmark_name=benchmark_name,
    debug_level=debug_level
  )

def task_runner_start_algorithm_on_all_benchmarks(algorithm_name, debug_level):
  return task_runner_start(
    'server.task_runner.run_all_benchmarks',
    algorithm_name=algorithm_name,
    debug_level=debug_level
  )

def task_runner_start_algorithm_on_custom_run(
  algorithm_name,
  benchmark_name,
  entry_name,
  debug_level
):
  return task_runner_start(
    'server.task_runner.run_custom_input',
    algorithm_name=algorithm_name,
    benchmark_name=benchmark_name,
    entry_name=entry_name,
    debug_level=debug_level
  )

def task_runner_start_algorithm_on_nqueens(
  algorithm_name,
  n,
  run_as_benchmark,
  timeout,
  debug_level
):
  return task_runner_start(
    'server.task_runner.run_nqueens',
    algorithm_name=algorithm_name,
    n=n,
    run_as_benchmark=run_as_benchmark,
    timeout=timeout,
    debug_level=debug_level
  )

def task_runner_get_progress(job_info, return_model=False):
  job = task_runner_get_job(job_info)
  job.refresh()
  value, model = None, None
  if 'interrupted' in job.meta and job.meta['interrupted']:
    value = 100
  elif 'finished' in job.meta and job.meta['finished']:
    value = 100
  elif not 'progress' in job.meta:
    value = 0
  else:
    value = job.meta['progress']

  if return_model:
    model = job.meta.get("model", None)
    return value, model
  else:
    return value

def task_runner_get_all_benchmarks_progress(job_info):
  job = task_runner_get_job(job_info)
  job.refresh()
  if 'interrupted' in job.meta and job.meta['interrupted']:
    return 100, None, True
  if 'finished' in job.meta and job.meta['finished']:
    return 100, None, True
  if not 'progress' in job.meta or not 'running_benchmark' in job.meta or not 'finished' in job.meta:
    return 0, None, False
  return job.meta['progress'], job.meta['running_benchmark'], job.meta['finished']

def has_job_finished(job):
  try:
    job.refresh()
    return job.meta["finished"]
  except:
    return False

def has_job_started(job: rq.job.Job):
  try:
    job.refresh()
    return "finished" in job.meta
  except Exception as e:
    return False

def get_job_log_file(job):
  job.refresh()
  if 'storage_file' not in job.meta:
    return None
  return job.meta["storage_file"]

def get_custom_run_log_file():
  log_filename = os.path.join(
    Config.SATSMT_RESULT_LOGS,
    Config.SATSOLVER_CUSTOM_RUN_FILENAME
  )

  if os.path.isfile(log_filename):
    return log_filename
  else:
    return None

def task_runner_stop_job(job:rq.job.Job):
  job.refresh()
  send_stop_job_command(get_redis_connection(), job.get_id())
  job.meta["interrupted"] = True
  job.save_meta()

def task_runner_get_job(job_info):
  return rq.job.Job.fetch(job_info["job"], connection=get_redis_connection())
