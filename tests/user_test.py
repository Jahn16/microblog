import pytest
from flask_login import FlaskLoginClient

from app.app import create_app
from app.db import db
from app.models.user import User


@pytest.fixture()
def app():
    config = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "TEST",
    }
    app = create_app(config)
    app.test_client_class = FlaskLoginClient
    with app.app_context():
        db.create_all()

    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def users(app):
    with app.app_context():
        users = [
            User(username=f"user{i}", email=f"user{i}@example.com")
            for i in range(3)
        ]
        db.session.add_all(users)
        db.session.commit()

        yield users


def test_profile_not_logged_in(app, client, users):
    with app.app_context():
        response = client.get(f"/profile/{users[0].username}")
        assert b"user-control" not in response.data
        assert b"follow-control" not in response.data


def test_profile_logged_in(app, users):
    with app.app_context():
        with app.test_client(user=users[0]) as client:
            response = client.get(f"/profile/{users[1].username}")
            assert b"user-control" not in response.data
            assert b"follow-control" in response.data


def test_own_profile(app, users):
    with app.app_context():
        user = users[0]
        with app.test_client(user=user) as client:
            response = client.get(f"/profile/{user.username}")
            assert b"user-control" in response.data
            assert b"follow-control" not in response.data


def test_follow(app, users):
    with app.app_context():
        with app.test_client(user=users[0]) as client:
            assert not users[0].is_following(users[1])
            response = client.post(
                "/follow_unfollow",
                data={"followed_id": users[1].id},
                follow_redirects=True,
            )
            assert len(response.history) == 1
            assert response.request.path == f"/profile/{users[1].username}"
            assert users[0].is_following(users[1])
            assert not users[1].is_following(users[0])


def test_unfollow(app, users):
    with app.app_context():
        users[0].follow(users[1])
        db.session.commit()
        with app.test_client(user=users[0]) as client:
            assert users[0].is_following(users[1])
            response = client.post(
                "/follow_unfollow",
                data={"followed_id": users[1].id},
                follow_redirects=True,
            )
            assert len(response.history) == 1
            assert response.request.path == f"/profile/{users[1].username}"
            assert not users[0].is_following(users[1])
