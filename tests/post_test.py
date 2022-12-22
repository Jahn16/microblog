import pytest
from flask_login import FlaskLoginClient

from app.app import create_app
from app.models.user import User
from app.models.post import Post
from app.db import db


@pytest.fixture()
def app():
    config = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "TEST",
    }
    app = create_app(config)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.test_client_class = FlaskLoginClient
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_post_not_logged_in(client):
    response = client.post("/post", follow_redirects=True)
    assert len(response.history) == 1
    assert response.request.path == "/login"


def test_post(app):
    with app.app_context():
        user = User(username="user", email="user@example.com")
        db.session.add(user)
        db.session.commit()
        with app.test_client(user=user) as client:
            response = client.post(
                "/post", data={"content": "TESTING"}, follow_redirects=True
            )
            assert response.request.path == "/"
            assert b"Enviado com sucesso." in response.data


def test_followed_posts_not_logged_in(client):
    response = client.get("/followed_posts", follow_redirects=True)
    assert len(response.history) == 1
    assert response.request.path == "/login"


def test_followed_posts(app):
    with app.app_context():
        users = [
            User(username=f"user{i}", email=f"user{i}@example.com")
            for i in range(3)
        ]
        db.session.add_all(users)
        posts = [
            Post(body=f"Post by {user.username}", author=user)
            for user in users
        ]
        db.session.add_all(posts)
        db.session.commit()
        with app.test_client(user=users[0]) as client:
            users[0].follow(users[2])
            response = client.get("/followed_posts")
            assert b"Post by user0" in response.data
            assert b"Post by user2" in response.data
            assert b"oist by user1" not in response.data
