from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

from app.db import get_db


db = get_db()

user_follower = db.Table(
    "user_follower",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    about_me = db.Column(db.String(140))
    following = db.relationship(
        "User",
        secondary=user_follower,
        primaryjoin=(user_follower.c.follower_id == id),
        secondaryjoin=(user_follower.c.user_id == id),
        backref=db.backref("user_follower", lazy="dynamic"),
        lazy="dynamic",
    )

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def is_following(self, user):
        print(bool(self.following.filter(user_follower.c.user_id == user.id).first()))
        return (
            self.following.filter(user_follower.c.user_id == user.id).first()
            is not None
        )

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)
            print("seguindo")

    def unfollow(self, user):
        print("called")
        if self.is_following(user):
            self.following.remove(user)

    def __repr__(self):
        return f"<User {self.username}>"
