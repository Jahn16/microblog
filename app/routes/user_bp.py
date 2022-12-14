from flask import Blueprint

from app.controllers.user_controller import profile, edit, follow_unfollow

user_bp = Blueprint("user_bp", __name__)

user_bp.route("/profile/<username>", methods=["GET"])(profile)
user_bp.route("/edit", methods=["GET", "POST"])(edit)
user_bp.route("/follow_unfollow", methods=["POST"])(follow_unfollow)
