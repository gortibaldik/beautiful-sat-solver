from server.config import Config

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logzero import logger

from server.config import Config

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DB_CONNECTION_STRING

logger.debug(f"DATABASE URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# disable some weird warning: https://github.com/pallets-eco/flask-sqlalchemy/pull/256
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# instantiate the database
db = SQLAlchemy(app)

# fighting circular imports
from server.views.benchmark_dashboard.page import benchmark_page
from server.views.benchmark_results.page import results_page
app.register_blueprint(benchmark_page, url_prefix='/benchmarks')
app.register_blueprint(results_page, url_prefix='/results')

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

from server.models import job
migrate = Migrate(app, db, directory=Config.MIGRATIONS_DIR)