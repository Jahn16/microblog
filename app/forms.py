from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    EmailField,
    TextAreaField,
    HiddenField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    ValidationError,
    Length,
    Email,
)

from app.models.user import User


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired("Insira um e-mail."),
            Email("Insira um e-mail válido."),
        ],
    )
    password = PasswordField(
        "Senha", validators=[DataRequired("Insira uma senha.")]
    )
    remember_me = BooleanField("Lembrar de mim")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Usuário", validators=[DataRequired("Insira um usuário.")]
    )
    email = EmailField(
        "Email",
        validators=[
            DataRequired("Insira um e-mail."),
            Email("Insira um e-mail válido."),
        ],
    )
    password = PasswordField(
        "Senha", validators=[DataRequired("Insira uma senha.")]
    )
    password_confirmation = PasswordField(
        "Confirme a senha",
        validators=[
            DataRequired("Confirme a senha."),
            EqualTo("password", message="As senhas não coincidem."),
        ],
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
    previous_username = HiddenField()
    username = StringField(
        "Usuário", validators=[DataRequired("Insira um usuário.")]
    )
    about_me = TextAreaField(
        "Descrição",
        validators=[
            DataRequired("Insira uma descrição."),
            Length(min=1, max=140),
        ],
    )

    def validate_username(self, username):
        if self.previous_username.data == self.username.data:
            return

        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Nome de usuário indisponível.")


class FollowForm(FlaskForm):
    followed_id = HiddenField()


class PostForm(FlaskForm):
    content = TextAreaField(
        "Diga algo",
        validators=[
            DataRequired("Insira uma mensagem."),
            Length(min=1, max=140),
        ],
    )


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired("Insira um e-mail."),
            Email("Insira um e-mail válido."),
        ],
    )


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        "Senha", validators=[DataRequired("Insira uma senha.")]
    )
    password_confirmation = PasswordField(
        "Confirme a senha",
        validators=[
            DataRequired("Confirme a nova senha."),
            EqualTo("password", message="As senhas não coincidem."),
        ],
    )
