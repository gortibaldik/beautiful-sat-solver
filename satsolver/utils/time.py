from timeit import default_timer as timer

def time_execution(function, *args, **kwargs):
  start = timer()
  result = function(*args, **kwargs)
  end = timer()
  return start, end, *result