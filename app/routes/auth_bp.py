from flask import Blueprint

from app.controllers.auth_controller import (
    login,
    logout,
    register,
    change_password,
    forgot_password,
)

auth_bp = Blueprint("auth_bp", __name__)

auth_bp.route("/login", methods=["GET", "POST"])(login)
auth_bp.route("/logout", methods=["GET"])(logout)
auth_bp.route("/register", methods=["GET", "POST"])(register)
auth_bp.route("/forgot_password", methods=["GET", "POST"])(forgot_password)
auth_bp.route("/change_password/<token>", methods=["GET", "POST"])(
    change_password
)
