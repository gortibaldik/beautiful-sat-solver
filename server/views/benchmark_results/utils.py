import random

def create_col(label, field, sort_asc=True, should_be_displayed=True, should_be_categorized=True):
  return {
    "label": label,
    "field": field,
    "sort": "asc" if sort_asc else "desc",
    "categorized": should_be_categorized,
    "displayed": should_be_displayed
  }

def create_row(algo, benchmark, time, derivations, unit_props):
  return {
    ALGO: algo,
    BENCHMARK: benchmark,
    AVERAGE_TIME: time,
    AVERAGE_DERIVATIONS: derivations,
    AVERAGE_UNIT_PROPS: unit_props
  }

def spawn_rows(number_of_rows: int):
  possible_algos = [ "dppl", "cdcl", "watching literals", "look forward"]
  possible_benchmarks = ["A", "B", "C", "D", "E"]
  max_time = 250
  max_derivs = 30
  max_unit_props = 200

  rows = []
  for _ in range(number_of_rows):
    rows.append(
      create_row(
        random.choice(possible_algos),
        random.choice(possible_benchmarks),
        random.random() * max_time,
        random.random() * max_derivs,
        random.random() * max_unit_props
      )
    )
  
  return rows

ALGO="algo"
BENCHMARK="benchmark"
AVERAGE_TIME="average_time"
AVERAGE_DERIVATIONS="average_derivations"
AVERAGE_UNIT_PROPS="average_unit_props"

def get_data():
  return {
    "columns": [
      create_col("Algorithm", ALGO),
      create_col("Benchmark", BENCHMARK),
      create_col("Average Time of Execution", AVERAGE_TIME, should_be_categorized=False),
      create_col("Average Number of Derivations", AVERAGE_DERIVATIONS, should_be_categorized=False),
      create_col("Average Number of Unit Propagations", AVERAGE_UNIT_PROPS, should_be_categorized=False),
    ],
    "rows": spawn_rows(5)
  }