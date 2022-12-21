from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import or_
from flask_login import current_user, login_required
from werkzeug.urls import url_parse

from app.models.post import Post
from app.forms import PostForm
from app.db import get_db


db = get_db()


def posts():
    form = PostForm()
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    if form.is_submitted():
        print("sadasdl")
    return render_template("index.html", posts=posts, form=form)


@login_required
def followed_posts():
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
            url_parse(request.host_url).netloc
            == url_parse(request.referrer).netloc
        )
        if is_url_safe:
            return redirect(request.referrer)
    return redirect(url_for("index"))
