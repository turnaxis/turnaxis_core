"""Default configuration"""

from dotenv import load_dotenv
import os

# load_dotenv()


class Config:
    """Default configuration"""

    # Authentication
    SECRET_KEY = ""
    AUTH_METHODS = [
        "Bearer",
    ]

    # API parameters
    API_TITLE = "BEMServer API"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_RAPIDOC_PATH = "/"
    OPENAPI_RAPIDOC_URL = "https://cdn.jsdelivr.net/npm/rapidoc/dist/rapidoc-min.js"
    OPENAPI_RAPIDOC_CONFIG = {
        "theme": "dark",
        "show-header": "false",
        "render-style": "focused",
        "allow-spec-file-download": "true",
        "show-components": "true",
    }

    # Profiling
    PROFILE_DIR = ""

    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    SQLALCHEMY_BINDS = {"db": os.getenv("SQLALCHEMY_DATABASE_URI")}

    ## MAIL SETTINGS

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 587
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    