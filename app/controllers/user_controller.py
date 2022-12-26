from flask import render_template, redirect, url_for, current_app as app
from flask_login import login_required, current_user

from app.db import get_db
from app.models.user import User
from app.models.post import Post
from app.forms import EditProfileForm, FollowForm
from app.utils.security import encode_url

db = get_db()


def profile(username):
    app.logger.info("Acessing {username} profile")
    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        Post.query.filter_by(user_id=user.id)
        .order_by(Post.timestamp.desc())
        .all()
    )
    form = FollowForm(data={"followed_id": user.id})
    return render_template(
        "profile.html", title=username, user=user, posts=posts, form=form
    )


@login_required
def edit():
    form = EditProfileForm(
        data={
            "previous_username": current_user.username,
            "username": current_user.username,
            "about_me": current_user.about_me,
        }
    )
    edit_password_token = encode_url(current_user.email, salt="recover-key")
    if form.validate_on_submit():
        app.logger.info(f"Editing user {current_user.username} profile")
        form.populate_obj(current_user)
        db.session.commit()
        return redirect(
            url_for("user_bp.profile", username=current_user.username)
        )
    return render_template(
        "edit.html",
        title="Editar Perfil",
        edit_password_token=edit_password_token,
        form=form,
    )


@login_required
def follow_unfollow():
    form = FollowForm()
    if form.validate_on_submit():
        if form.followed_id.data == current_user.id:
            return redirect(
                url_for("user_bp.profile", username=current_user.username)
            )

        followed_user = User.query.get(form.followed_id.data)
        if not followed_user:
            return redirect(url_for("index"))

        if not current_user.is_following(followed_user):
            app.logger.info(
                f"User {current_user.username} "
                f"followed {followed_user.username}"
            )
            current_user.follow(followed_user)
        else:
            app.logger.info(
                f"User {current_user.username} "
                f"unfollowed {followed_user.username}"
            )
            current_user.unfollow(followed_user)
        db.session.commit()
        return redirect(
            url_for("user_bp.profile", username=followed_user.username)
        )
    return redirect(url_for("index"))
