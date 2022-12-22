from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user

from app.models.user import User
from app.utils.email import send_email
from app.forms import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    ForgotPasswordForm,
)
from app.utils.security import encode_url, decode_url, is_url_safe
from app.db import get_db

db = get_db()


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
        if next_page and is_url_safe(next_page):
            return redirect(next_page, code=307)
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)


def logout():
    logout_user()
    return redirect(url_for("index"))


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
        return redirect(url_for("auth_bp.login"))
    return render_template("register.html", title="Cadastro", form=form)


def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = encode_url(user.email, salt="recover-key")

            send_email(
                subject="Redefinição de senha",
                recipients=[user.email],
                html_body=render_template(
                    "email/forgot_password.html", token=token, user=user
                ),
            )
        return redirect(url_for("index"))
    return render_template("forgot_password.html", form=form)


def change_password(token):
    email = decode_url(token, salt="recover-key", max_age=86400)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        user.set_password(form.password.data)
        db.session.commit()
        logout_user()
        flash("Sua senha foi redefinada com sucesso.", category="success")
        return redirect(url_for("auth_bp.login"))
    return render_template("change_password.html", form=form)
