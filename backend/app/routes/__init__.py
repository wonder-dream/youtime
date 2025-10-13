from .users import user_bp as users_bp
from .tasks import task_bp as tasks_bp

def register_blueprints(app):
    '''
    注册所有蓝图
    这个函数将所有的蓝图注册到Flask应用实例中。
    '''
    app.register_blueprint(users_bp)
    app.register_blueprint(tasks_bp)
