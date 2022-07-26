import os

from logzero import logger
from server.config import Config
from server.views.benchmark_dashboard.utils import benchmark_name_sorting_criterion

def get_benchmarks():
  benchmark_root = Config.SATSMT_BENCHMARK_ROOT
  benchmark_names = list(os.listdir(benchmark_root))
  benchmarks = []
  for b in sorted(benchmark_names, key=benchmark_name_sorting_criterion):
    benchmark_dir = os.path.join(benchmark_root, b)
    benchmark_inputs = list(os.listdir(benchmark_dir))
    
    benchmark_inputs_sorted = sorted(benchmark_inputs, key=benchmark_name_sorting_criterion)
    
    benchmark_entry = {
      "name": b,
      "inputs": benchmark_inputs_sorted
    }

    benchmarks.append(benchmark_entry)
  return benchmarks

