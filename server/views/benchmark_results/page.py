from flask import Blueprint, jsonify, request
from server.utils.exception_utils import on_exception_result_failure, on_success_result_success
from server.utils.log_utils import get_log_file_content, remove_log_file
from server.views.benchmark_results.utils import get_data

results_page = Blueprint('results_page', __name__)

@results_page.route('/', methods=['GET'])
@on_exception_result_failure
def results_index():
  return jsonify(get_data())

@results_page.route('/get_log_file', methods=['POST'])
@on_exception_result_failure
def get_log_file():
  return jsonify({
    "result": get_log_file_content(request.get_json()["log_file"])
  })

@results_page.route('/remove_log_file', methods=['POST'])
@on_exception_result_failure
@on_success_result_success
def remove_path():
  remove_log_file(request.get_json()["log_file"])
