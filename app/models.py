from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

from app.app import db, login

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
        return self.following.filter(user_follower.c.user_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
    
    def following_posts(self):
        return Post.query.join(user_follower, (user_follower.c.user_id == Post.user_id)).filter(user_follower.c.user_id == self.id).order_by(Post.timestamp.desc())
    def __repr__(self):
        return f"<User {self.username}>"


@login.user_loader
def load_user(id: str):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f"<Post {self.body}>"
