from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_db():
    db.init_app(current_app._get_current_object())
    migrate.init_app(current_app)


def get_db():
    return db
