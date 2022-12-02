from flask import render_template

from app.app import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", error_message="Página não encontrada"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return (
        render_template("error.html", error_message="Um erro inesperado ocorreu"),
        500,
    )
