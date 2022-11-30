from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length

from app.app import User


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(message="Insira um e-mail.")])
    password = PasswordField(
        "Senha", validators=[DataRequired(message="Insira uma senha.")]
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


class EditProfileForm(FlaskForm):
    username = StringField(
        "Usuário", validators=[DataRequired(message="Insira um usuário")]
    )
    about_me = TextAreaField("Descrição", validators=[Length(min=0, max=140)])
