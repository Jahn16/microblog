from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from app.app import User


class LoginForm(FlaskForm):
    username = StringField(
        "Usuário", validators=[DataRequired(message="Insira um usuário")]
    )
    password = PasswordField(
        "Senha", validators=[DataRequired(message="Insira uma senha")]
    )
    remember_me = BooleanField("Lembrar de mim")


class RegistrationForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    password_confirmation = PasswordField(
        "Confirme a senha", validators=[DataRequired(), EqualTo("password")]
    )

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Nome de usuário já utilizado.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email já cadastrado.")
