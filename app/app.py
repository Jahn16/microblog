import json

from flask import Flask
from flask_moment import Moment

from app.db import init_db
from app.login import init_login_manager
from app.utils.email import init_mail
from app.routes.post_bp import post_bp
from app.routes.auth_bp import auth_bp
from app.routes.user_bp import user_bp
from app.routes.error_bp import error_bp


moment = Moment()


def create_app(test_config=None):
    app = Flask(__name__)
    if not test_config:
        app.config.from_file("../config.json", load=json.load)
    else:
        app.config.from_mapping(test_config)

    with app.app_context():
        init_db()
        init_login_manager()
        init_mail()
    moment.init_app(app)

    app.register_blueprint(post_bp)
    app.add_url_rule("/", endpoint="index")
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(error_bp)
    return app
