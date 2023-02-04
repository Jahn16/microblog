from flask import current_app
from flask_mail import Mail, Message

mail = Mail()


def init_mail():
    mail.init_app(current_app)


def send_email(subject: str, recipients: list[str], html_body: str):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    mail.send(msg)
