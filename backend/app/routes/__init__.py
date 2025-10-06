from .users import bp as users_bp
from .tasks import bp as tasks_bp

def register_blueprints(app):
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
