import traceback

from flask import Blueprint, jsonify
from logzero import logger
from server.views.benchmark_results.utils import get_data

results_page = Blueprint('results_page', __name__)

@results_page.route('/', methods=['GET'])
def results_index():
  try:
    return jsonify(get_data())
  except:
    logger.warning(traceback.format_exc())
    return jsonify({ 'result': 'failure'})

