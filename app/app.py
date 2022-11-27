import json

from flask import Flask
from flask import render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.forms import LoginForm

app = Flask(__name__)
app.config.from_file("../config.json", load=json.load)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


@app.route("/")
@app.route("/index")
def index():
    user = {"username": "Jahn"}
    posts = [
        {"author": {"username": "John"}, "body": "Belo dia em BH!"},
        {"author": {"username": "Susan"}, "body": "Boa vitoria Brasileira!"},
    ]
    return render_template("index.html", title="Home", user=user, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Requisitado entrada de usuário {form.username.data}")
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)
