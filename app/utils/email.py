from flask_mail import Message

from app.app import mail


def send_email(subject: str, recipients: list[str], html_body: str):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    mail.send(msg)
