from flask import Flask, jsonify
from flask_cors import CORS

import server.getters

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/algorithms', methods=['GET'])
def get_benchmarks():
  benchmarks = [a for a in algorithms_infos if a["benchmarkable"]]
  return jsonify(benchmarks)


if __name__ == '__main__':
  algorithms = server.getters.get_modules()
  algorithms_infos = [a.get_info() for a in algorithms.values()]
  app.run()
