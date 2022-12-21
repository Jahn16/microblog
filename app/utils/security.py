from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from werkzeug.urls import url_parse


def get_url_serializer():
    return URLSafeTimedSerializer(current_app.config)


def encode_url(obj: str, salt: str = ""):
    url_serializer = get_url_serializer()
    return url_serializer.dumps(obj, salt=salt)


def decode_url(obj: str, salt: str = "", max_age: int = 18000):
    url_serializer = get_url_serializer()
    return url_serializer.loads(obj, salt=salt, max_age=max_age)


def is_url_safe(url: str, host_url: str = ""):
    parsed_url = url_parse(url)
    if not parsed_url.netloc:
        return True

    parsed_host_url = url_parse(host_url)
    return parsed_url.netloc == parsed_host_url.netloc
