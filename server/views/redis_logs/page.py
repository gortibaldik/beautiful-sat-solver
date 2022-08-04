from flask import Blueprint, jsonify
from server.utils.exception_utils import on_exception_result_failure, on_success_result_success
from server.views.redis_logs.utils import get_data
from server.utils.log_utils import clear_redis_error_logs, clear_redis_std_logs

redis_logs_page = Blueprint('redis_logs_page', __name__)

@redis_logs_page.route('/', methods=['GET'])
@on_exception_result_failure
def results_index():
  return jsonify(get_data())

@redis_logs_page.route('/clear_std', methods=['GET'])
@on_exception_result_failure
@on_success_result_success
def clear_std():
  clear_redis_std_logs()

@redis_logs_page.route('/clear_error', methods=['GET'])
@on_exception_result_failure
@on_success_result_success
def clear_error():
  clear_redis_error_logs()