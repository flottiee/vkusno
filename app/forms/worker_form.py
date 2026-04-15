from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, TelField
from wtforms.validators import DataRequired


class WorkerCheckPassForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
