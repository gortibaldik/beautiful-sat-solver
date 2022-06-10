import asyncio
import pickle
import redis
import server.getters

from flask import Flask
from flask_cors import CORS

from satsolver.benchmark_preparation.benchmark_downloader import download_all_not_downloaded_benchmarks
from server.views.benchmark_dashboard.page import benchmark_page
from server.views.benchmark_dashboard.utils import set_algorithms_infos, set_saved_jobs

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.register_blueprint(benchmark_page)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

if __name__ == '__main__':
  asyncio.run(download_all_not_downloaded_benchmarks())
  algorithms = server.getters.get_modules()
  algorithms_infos = [a.get_info() for a in algorithms.values()]
  saved_jobs = {}
  with redis.Redis.from_url('redis://') as connection:
    set_algorithms_infos(algorithms_infos, connection)
    set_saved_jobs(saved_jobs, connection)
  app.run()
