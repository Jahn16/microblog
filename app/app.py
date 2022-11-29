import json

from flask import Flask
from flask import render_template, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from werkzeug.urls import url_parse


app = Flask(__name__)
app.config.from_file("../config.json", load=json.load)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

from app.models import User, Post
from app.forms import LoginForm, RegistrationForm

login.login_view = "login"


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post}


@app.route("/")
@app.route("/index")
def index():
    posts = Post.query.all()
    return render_template("index.html", title="Home", posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash("Credenciais inválidas", "danger")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if next_page and not url_parse(next_page).netloc:
            return url_for(next_page)
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Usuário registrado com sucesso!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Cadastro", form=form)
