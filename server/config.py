import os

class Config:
  SATSMT_BENCHMARK_ROOT="satsolver/benchmarks/"
  BENCHMARKED_RESULTS_AVAILABILITY=35000 # milliseconds
  SATSMT_RESULT_LOGS="server/result_logs/"
  DUMMY_RUNTIME=5 # seconds
  DB_CONNECTION_STRING="postgresql://postgres:{}@{}:5432/satsolverdb".format(os.getenv("DB_PASSWORD") or "password", os.getenv("DB_IP_ADDRESS"))
  MIGRATIONS_DIR=os.getenv("DB_MIGRATIONS_DIR")
