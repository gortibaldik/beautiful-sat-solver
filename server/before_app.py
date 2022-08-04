import asyncio

from satsolver.benchmark_preparation.benchmark_downloader import download_all_not_downloaded_benchmarks
from server.config import Config
import server.getters
from server.utils.redis_utils import get_redis_connection, set_algorithms_infos, set_saved_jobs

if __name__ == '__main__':
  asyncio.run(download_all_not_downloaded_benchmarks())
  algorithms = server.getters.get_modules()
  algorithms_infos = [a.get_info() for a in algorithms.values()]
  saved_jobs = {}
  print(f"environment: {Config.APP_ENVIRONMENT}")
  with get_redis_connection() as connection:
    set_algorithms_infos(algorithms_infos, connection)
    set_saved_jobs(saved_jobs, connection)