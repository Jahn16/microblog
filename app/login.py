from flask import current_app
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"
login_manager.login_message_category = "danger"
login_manager.login_message = "Faça o login  para acessar esta página."


def init_login_manager():
    login_manager.init_app(current_app)


def get_login_manager():
    return login_manager
