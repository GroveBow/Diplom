from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
#from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, number_range


class OrderAppendForm(FlaskForm):
    weight = StringField('Вес', validators=[DataRequired(), number_range(range(0, 50))])
    region = SelectField("Регион",
                         choices=[('1', 'Войковский'), ('2', 'Головинский'), ('3', 'Чеховский'),
                                  ('4', 'Щелковский')])
    delivery_hours = SelectMultipleField("Удобное время доставки",
                                        choices=[('08:00-11:00', '08:00-11:00'), ('11:00-14:00', '11:00-14:00'),
                                                 ('14:00-17:00', '14:00-17:00'), ('17:00-20:00', '17:00-20:00'),
                                                 ('20:00-23:00', '20:00-23:00'),
                                                 ('23:00-02:00', '23:00-02:00'),
                                                 ('02:00-05:00', '02:00-05:00'),
                                                 ('05:00-08:00', '05:00-08:00')])
    submit = SubmitField('Добавить')
    update = SubmitField('Обновить')
