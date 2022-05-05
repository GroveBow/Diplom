from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class ConfirmForm(FlaskForm):
    submit = SubmitField('Вернуться в меню')