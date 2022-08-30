from flask import Blueprint, jsonify
from server.utils.exception_utils import (
  on_exception_result_failure,
)
from server.utils.redis_utils import get_algorithms_infos, get_redis_connection, get_saved_jobs
from server.views.n_queens.utils import get_running_nqueens

n_queens_page = Blueprint('n_queens_page', __name__)

@n_queens_page.route('/', methods=['GET'])
@on_exception_result_failure
def n_queens_index(): 
  with get_redis_connection() as connection:
    algorithms_infos = get_algorithms_infos(connection)
    saved_jobs = get_saved_jobs(connection)
  # logger.info(algorithms_infos)
  # logger.info(saved_jobs)
  benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
  return jsonify({
    "result": "success",
    "algorithms": benchmarkable_algorithms,
    "running_job": get_running_nqueens(saved_jobs)
  })