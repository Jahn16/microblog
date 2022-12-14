from flask import Blueprint

from app.controllers.post_controller import posts, followed_posts, post

post_bp = Blueprint("post_bp", __name__)

post_bp.route("/", methods=["GET"])(posts)
post_bp.route("/followed_posts", methods=["GET"])(followed_posts)
post_bp.route("/post", methods=["POST"])(post)
