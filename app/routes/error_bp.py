from flask import Blueprint, render_template

from app.db import get_db

error_bp = Blueprint("error_bp", __name__)


@error_bp.app_errorhandler(404)
def not_found_error(error):
    return (
        render_template("error.html", error_message="Página não encontrada"),
        404,
    )


@error_bp.app_errorhandler(500)
def internal_error(error):
    db = get_db()
    db.session.rollback()

    return (
        render_template(
            "error.html", error_message="Um erro inesperado ocorreu"
        ),
        500,
    )
