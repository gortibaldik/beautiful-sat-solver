from flask import Flask, jsonify, request
from flask_cors import CORS
from logzero import logger

import server.getters
from server.task_runner import get_benchmark_progress, start_algorithm_on_benchmark
from server.app_utils import get_post_data, get_environ, retrieve_log_file, get_running_status, get_benchmark_names, save_job

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/algorithms', methods=['GET'])
def algorithm_index():
  try:
    benchmarkable_algorithms = [a for a in algorithms_infos if a["benchmarkable"]]
    benchmarked_result_availability = int(get_environ("BENCHMARKED_RESULTS_AVAILABILITY"))
    return jsonify({
      "response": "success",
      "benchmarks": get_benchmark_names(),
      "benchmarkable_algorithms_running_status": get_running_status(benchmarkable_algorithms, saved_jobs),
      "benchmarkable_algorithms": benchmarkable_algorithms,
      "benchmarked_result_availability": benchmarked_result_availability - 5000
    })
  except:
    return jsonify({ 'response': 'failure'})

@app.route('/start_algorithm', methods=['POST'])
def start_algorithm():
  try:
    algorithm_name, benchmark_name = get_post_data()
    job = start_algorithm_on_benchmark(algorithm_name, benchmark_name)
    save_job(job, algorithm_name, benchmark_name, saved_jobs)
  except:
    return jsonify({ 'response': 'failure'})
  return jsonify({ 'response': 'success' })

@app.route('/get_progress', methods=['POST'])
def get_progress():
  try:
    algorithm_name, benchmark_name = get_post_data()
    progress = get_benchmark_progress(saved_jobs[f"{algorithm_name},{benchmark_name}"]["job"])
  except Exception as e:
    logger.warning(e)
    return jsonify({'progress': 'error'})
  return jsonify({'progress': progress})

@app.route('/get_result', methods=['POST'])
def get_result():
  try:
    algorithm_name, benchmark_name = get_post_data()
    return jsonify({ "result" : retrieve_log_file(saved_jobs[f"{algorithm_name},{benchmark_name}"]) })
  except:
    return jsonify({ 'result': 'failure'})

if __name__ == '__main__':
  algorithms = server.getters.get_modules()
  algorithms_infos = [a.get_info() for a in algorithms.values()]
  saved_jobs = {}
  app.run()
