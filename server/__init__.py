from flask import Flask
from flask_cors import CORS

from server.views.benchmark_dashboard.page import benchmark_page
from server.views.benchmark_results.page import results_page

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.register_blueprint(benchmark_page, url_prefix='/benchmarks')
app.register_blueprint(results_page, url_prefix='/results')

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})