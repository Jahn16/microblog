import json

from flask import Flask
from flask import render_template, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_mail import Mail
from flask_moment import Moment
from werkzeug.urls import url_parse
from itsdangerous import URLSafeTimedSerializer


app = Flask(__name__)
app.config.from_file("../config.json", load=json.load)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
mail = Mail(app)
moment = Moment(app)
url_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

from app import errors
from app.models.user import User
from app.models.post import Post
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    FollowForm,
    PostForm,
    ForgotPasswordForm,
    ChangePasswordForm,
)
from app.routes.post_bp import post_bp
from app.routes.auth_bp import auth_bp
from app.routes.user_bp import user_bp

app.register_blueprint(post_bp)
app.add_url_rule("/", endpoint="index")

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

login.login_view = "auth_bp.login"
login.login_message_category = "danger"
login.login_message = "Faça o login  para acessar esta página."


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post}



