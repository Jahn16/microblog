from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app.db import get_db
from app.models.user import User
from app.forms import EditProfileForm, FollowForm
from app.utils.security import encode_url

db = get_db()


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
            current_user.follow(followed_user)
        else:
            current_user.unfollow(followed_user)
        db.session.commit()
        return redirect(
            url_for("user_bp.profile", username=followed_user.username)
        )
    return redirect(url_for("post_bp.index"))
