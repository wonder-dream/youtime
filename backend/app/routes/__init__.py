from .users import user_bp as users_bp
from .tasks import task_bp as tasks_bp

def register_blueprints(app):
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
