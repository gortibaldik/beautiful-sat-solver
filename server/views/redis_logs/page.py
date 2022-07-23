import traceback

from flask import Blueprint, jsonify, request
from logzero import logger
from server.utils.log_utils import get_log_file_content, remove_log_file
from server.views.redis_logs.utils import get_data

redis_logs_page = Blueprint('redis_logs_page', __name__)

@redis_logs_page.route('/', methods=['GET'])
def results_index():
  try:
    return jsonify(get_data())
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})