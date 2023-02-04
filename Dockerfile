FROM python:3.9-slim as build

WORKDIR /usr/app
RUN python -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.9-slim@sha256:9e0b4391fc41bc35c16caef4740736b6b349f6626fd14eba32793ae3c7b01908

RUN groupadd -g 999 user && useradd -r -u 999 -g user user

RUN mkdir /usr/app && chown user:user /usr/app
WORKDIR /usr/app

COPY --chown=user:user --from=build /usr/app/venv ./venv
COPY --chown=user:user . .
USER 999

ENV PATH="/usr/app/venv/bin:$PATH"
ENV FLASK_APP="app/app.py"


CMD flask db upgrade && gunicorn --bind 0.0.0.0:5000 -w 3 "app.app:create_app()"


