from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField
#from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    submit = SubmitField('Войти')
    #type = SelectField("Тип", choices=[(0, 'Курьер'), (2, 'Пользователь')], validators=[DataRequired()])