"""BEMServer API"""

import importlib

import flask
from werkzeug.middleware.profiler import ProfilerMiddleware
from dotenv import load_dotenv
from bemserver_core import BEMServerCore
from .extensions.email import mail

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
from .models import db
from bemserver_core.celery import celery
from .tasks import send_email
from flask_cors import CORS

# API_VERSION = importlib.metadata.version("bemserver-api")
API_VERSION = "0.24.0"
OPENAPI_VERSION = "3.1.0"
load_dotenv()
def create_app():
    """Create application"""
    app = flask.Flask(__name__)
    app.config.from_object("bemserver_api.settings.Config")
    app.config.from_envvar("BEMSERVER_API_SETTINGS_FILE", silent=True)
    CORS(app)

    db.init_app(app)
    database.init_app(app)
    
    mail.init_app(app)

    with app.app_context():
        db.create_all()

    from .models import Token
    
    api = Api(
        spec_kwargs={
            "version": API_VERSION,
            "openapi_version": OPENAPI_VERSION,
        }
    )
    api.init_app(app)
    authentication.auth.init_app(app)
    register_blueprints(api)
    celery.autodiscover_tasks()
    BEMServerCore()


    if profile_dir := app.config["PROFILE_DIR"]:
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app, stream=None, profile_dir=profile_dir
        )

    return app
