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

from app import errors
from app.models import User, Post
from app.forms import (
    LoginForm,
    RegistrationForm,
    EditProfileForm,
    FollowForm,
    PostForm,
    ForgotPasswordForm,
    ChangePasswordForm,
)
from app.email import send_email


login.login_view = "login"
login.login_message_category = "danger"
login.login_message = "Faça o login  para acessar esta página."

url_serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Post": Post}


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET", "POST"])
def index():
    form = PostForm()
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    if form.is_submitted():
        print("sadasdl")
    return render_template("index.html", posts=posts, form=form)


@app.route("/following", methods=["GET"])
@login_required
def following():
    form = PostForm()
    page = request.args.get("page", 1, type=int)
    posts = (
        Post.query.filter(
            or_(
                Post.user_id.in_([user.id for user in current_user.following]),
                Post.user_id.__eq__(current_user.id),
            )
        )
        .order_by(Post.timestamp.desc())
        .paginate(page=page, per_page=6, error_out=False)
    )
    form = PostForm()
    return render_template("following.html", posts=posts, form=form)


@app.route("/post", methods=["POST"])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Enviado com sucesso.")

    if request.referrer:
        if url_parse(request.referrer).path == "login":
            return redirect(url_for("index"))

        is_url_safe = (
            url_parse(request.host_url).netloc == url_parse(request.referrer).netloc
        )
        if is_url_safe:
            return redirect(request.referrer)
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.check_password(form.password.data):
            flash("Credenciais inválidas", "danger")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if next_page and not url_parse(next_page).netloc:
            return redirect(next_page, code=307)
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


@app.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {"id": 1, "author": user, "body": "Test post #1"},
        {"id": 2, "author": user, "body": "Test post #2"},
    ]
    form = FollowForm(data={"followed_id": user.id})
    return render_template(
        "profile.html", title=username, user=user, posts=posts, form=form
    )


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    form = EditProfileForm(
        data={
            "previous_username": current_user.username,
            "username": current_user.username,
            "about_me": current_user.about_me,
        }
    )
    edit_password_token = url_serializer.dumps(current_user.email, salt="recover-key")
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        return redirect(url_for("profile", username=current_user.username))
    return render_template(
        "edit.html",
        title="Editar Perfil",
        edit_password_token=edit_password_token,
        form=form,
    )


@app.route("/follow_unfollow", methods=["POST"])
@login_required
def follow_unfollow():
    form = FollowForm()
    if form.validate_on_submit():
        if form.followed_id.data == current_user.id:
            return redirect(url_for("profile", username=current_user.username))

        followed_user = User.query.get(form.followed_id.data)
        if not followed_user:
            return redirect(url_for("index"))

        if not current_user.is_following(followed_user):
            current_user.follow(followed_user)
        else:
            current_user.unfollow(followed_user)
        db.session.commit()
        return redirect(url_for("profile", username=followed_user.username))
    return redirect(url_for("index"))


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = url_serializer.dumps(user.email, salt="recover-key")

            send_email(
                subject="Redefinição de senha",
                recipients=[user.email],
                html_body=render_template(
                    "email/forgot_password.html", token=token, user=user
                ),
            )
        return redirect(url_for("index"))
    return render_template("forgot_password.html", form=form)


@app.route("/change_password/<token>", methods=["GET", "POST"])
def change_password(token):
    email = url_serializer.loads(token, salt="recover-key", max_age=86400)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        user.set_password(form.password.data)
        db.session.commit()
        logout_user()
        flash("Sua senha foi redefinada com sucesso.", category="success")
        return redirect(url_for("login"))
    return render_template("change_password.html", form=form)
