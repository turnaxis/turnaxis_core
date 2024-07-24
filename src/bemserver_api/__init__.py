"""BEMServer API"""

import importlib

import flask
from werkzeug.middleware.profiler import ProfilerMiddleware
import sys
import os
from flask_cors import CORS
# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add the submodule's path to sys.path
sys.path.insert(0, os.path.join(parent_dir))

from bemserver_core import BEMServerCore

from . import database
from .extensions import (  # noqa
    Api,
    AutoSchema,
    Blueprint,
    Schema,
    SQLCursorPage,
    authentication,
)
from .resources import register_blueprints

# API_VERSION = importlib.metadata.version("bemserver-api")
API_VERSION = "0.24.0"
OPENAPI_VERSION = "3.1.0"


def create_app():
    """Create application"""
    app = flask.Flask(__name__)
    app.config.from_object("bemserver_api.settings.Config")
    app.config.from_envvar("BEMSERVER_API_SETTINGS_FILE", silent=True)
    CORS(app)
    database.init_app(app)
    api = Api(
        spec_kwargs={
            "version": API_VERSION,
            "openapi_version": OPENAPI_VERSION,
        }
    )
    api.init_app(app)
    authentication.auth.init_app(app)
    register_blueprints(api)

    BEMServerCore()

    if profile_dir := app.config["PROFILE_DIR"]:
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app, stream=None, profile_dir=profile_dir
        )

    return app
