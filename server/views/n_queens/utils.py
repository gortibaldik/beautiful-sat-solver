from server.get_running_job import RunningJobType, find_running_job


def get_running_nqueens(saved_jobs):
  key, result = find_running_job(saved_jobs)
  if result is None or result != RunningJobType.NQUEENS:
    return { "algorithm": "none" }
  else:
    algo, problem, descr1, descr2 = key.split(",")
    return {
      "algorithm": algo,
      "problem":   problem,
      "N":         descr1,
      "timeout":   descr2
    }