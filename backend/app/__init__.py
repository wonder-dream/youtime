from flask import Flask
from .routes import register_blueprints
import secrets


def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)
    register_blueprints(app)

    return app
