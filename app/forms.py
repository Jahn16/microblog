from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(
        "Usuário", validators=[DataRequired(message="Insira um usuário")]
    )
    password = PasswordField(
        "Senha", validators=[DataRequired(message="Insira uma senha")]
    )
    remember_me = BooleanField("Lembrar Usuário")
