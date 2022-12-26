from flask import (
    request,
    render_template,
    redirect,
    url_for,
    flash,
    current_app as app,
)
from sqlalchemy import or_
from flask_login import current_user, login_required

from app.models.post import Post
from app.forms import PostForm
from app.db import get_db
from app.utils.security import is_url_safe


db = get_db()


def posts():
    form = PostForm()
    page = request.args.get("page", 1, type=int)
    app.logger.info(f"Retrieving all posts in page {page}")
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    return render_template("index.html", posts=posts, form=form)


@login_required
def followed_posts():
    form = PostForm()
    page = request.args.get("page", 1, type=int)
    app.logger.info(f"Retrieving followed posts by {current_user.username}")
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
    return render_template(
        "following.html", title="Seguidas", posts=posts, form=form
    )


@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.content.data, author=current_user)
        app.logger.info(f"User {current_user.username} posted")
        db.session.add(post)
        db.session.commit()
        flash("Enviado com sucesso.", category="validation")

    if request.referrer:
        if is_url_safe(request.referrer, request.host_url):
            return redirect(request.referrer)
    return redirect(url_for("index"))
