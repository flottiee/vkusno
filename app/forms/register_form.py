from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    surname = StringField('Ваша фамилия', validators=[DataRequired()])
    name = StringField('Ваше имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    speciality = SelectField("Выберете специальность:", choices=[('chef', 'Повар'), ('courier', 'курьер'),
                                                                 ('customer', 'Клиент'), ('admin', 'Администратор'),
                                                                 ('programmer', 'Разработчик')],
                             validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
