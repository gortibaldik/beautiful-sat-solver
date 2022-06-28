import traceback

from flask import Blueprint, jsonify, request
from logzero import logger
from server.views.benchmark_results.utils import get_data, get_log_file_content, remove_log_file

results_page = Blueprint('results_page', __name__)

@results_page.route('/', methods=['GET'])
def results_index():
  try:
    return jsonify(get_data())
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})

@results_page.route('/get_log_file', methods=['POST'])
def get_log_file():
  try:
    return jsonify({
        "result": get_log_file_content(request.get_json()["log_file"])
    })
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})

@results_page.route('/remove_log_file', methods=['POST'])
def remove_path():
  try:
    remove_log_file(request.get_json()["log_file"])
    return jsonify({
      "result": "success"
    })
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})
