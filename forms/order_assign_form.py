from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
#from wtforms.fields.html5 import EmailField
#from wtforms.validators import DataRequired


class OrderAssignForm(FlaskForm):
    submit = SubmitField('Войти')