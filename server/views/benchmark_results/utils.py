import random

def create_col(label, field, sort_asc=True):
  return {
    "label": label,
    "field": field,
    "sort": "asc" if sort_asc else "desc"
  }

def create_row(algo, benchmark, time):
  return {
    ALGO: algo,
    BENCHMARK: benchmark,
    AVERAGE_TIME: time
  }

def spawn_rows(number_of_rows: int):
  possible_algos = [ "dppl", "cdcl", "watching literals", "look forward"]
  possible_benchmarks = ["A", "B", "C", "D", "E"]
  max_time = 250

  rows = []
  for _ in range(number_of_rows):
    rows.append(
      create_row(
        random.choice(possible_algos),
        random.choice(possible_benchmarks),
        random.random() * max_time
      )
    )
  
  return rows

ALGO="algo"
BENCHMARK="benchmark"
AVERAGE_TIME="average_time"

def get_data():
  return {
    "columns": [
      create_col("Algorithm", ALGO),
      create_col("Benchmark", BENCHMARK),
      create_col("Average Time of Execution", AVERAGE_TIME)
    ],
    "rows": spawn_rows(80)
  }