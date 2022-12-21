from flask import current_app

from itsdangerous import URLSafeTimedSerializer


def get_url_serializer():
    return URLSafeTimedSerializer(current_app.config)


def encode_url(obj: str, salt: str = ""):
    url_serializer = get_url_serializer()
    return url_serializer.dumps(obj, salt=salt)


def decode_url(obj: str, salt: str = "", max_age: int = 18000):
    url_serializer = get_url_serializer()
    return url_serializer.loads(obj, salt=salt, max_age=max_age)
