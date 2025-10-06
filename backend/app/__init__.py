from flask import Flask
from .routes import register_blueprints

def create_app():
    app = Flask(__name__)
    register_blueprints(app)
    
    return app