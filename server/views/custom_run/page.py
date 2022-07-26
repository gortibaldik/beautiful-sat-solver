import traceback

from flask import Blueprint, jsonify
from logzero import logger

from server.utils.redis_utils import (
  get_algorithms_infos,
  get_saved_jobs,
  get_redis_connection,
)
from server.views.custom_run.utils import (
  get_benchmarks,
)

custom_run_page = Blueprint('custom_run_page', __name__)

@custom_run_page.route('/', methods=['GET'])
def algorithm_index():
  try:
    with get_redis_connection() as connection:
      algorithms_infos = get_algorithms_infos(connection)
    # logger.info(algorithms_infos)
    # logger.info(saved_jobs)
    benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
    return jsonify({
      "result": "success",
      "benchmarks": get_benchmarks(),
      "algorithms": benchmarkable_algorithms,
    })
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})
