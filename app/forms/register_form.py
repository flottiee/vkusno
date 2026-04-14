from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, TelField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия')
    name = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    phone = TelField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
