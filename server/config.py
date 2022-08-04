import logzero
import os

class Config:
  SATSMT_BENCHMARK_ROOT="satsolver/benchmarks/" if os.getenv("APP_ENVIRONMENT") != "PROD" else "benchmarks/"
  BENCHMARKED_RESULTS_AVAILABILITY=35000 # milliseconds
  SATSMT_RESULT_LOGS="logs/result_logs/"
  SATSOLVER_REDIS_LOGS=os.getenv("SATSOLVER_REDIS_LOGS")
  SATSOLVER_REDIS_ERROR_FILENAME=os.getenv("SATSOLVER_REDIS_ERROR_FILENAME")
  SATSOLVER_REDIS_STD_FILENAME=os.getenv("SATSOLVER_REDIS_STD_FILENAME")
  SATSOLVER_CUSTOM_RUN_FILENAME="custom_run.log"
  DB_CONNECTION_STRING="postgresql://postgres:{}@{}:5432/satsolverdb".format(os.getenv("DB_PASSWORD") or "password", os.getenv("DB_IP_ADDRESS"))
  MIGRATIONS_DIR=os.getenv("DB_MIGRATIONS_DIR")
  DEFAULT_LOGLEVEL=logzero.INFO
  NNF_REDUCE_IMPLICATIONS=True
  APP_ENVIRONMENT=os.getenv("APP_ENVIRONMENT")
  REDIS_HOSTNAME="redis"
  REDIS_WORKER_QUEUE_NAME=os.getenv("REDIS_QUEUE_NAME")
