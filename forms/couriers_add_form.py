from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, SelectMultipleField
#from wtforms.fields.html5 import EmailField
#from wtforms.validators import DataRequired


class CourierAddForm(FlaskForm):
    type = SelectField("Тип курьера",
                                  choices=[('foot', 'Пеший'), ('bike', 'Велосипед'), ('car', 'Машина')])
    regions = SelectMultipleField("Регионы",
                                  choices=[('1', 'Войковский'), ('2', 'Головинский'), ('3', 'Чеховский'),
                                           ('4', 'Щелковский')])
    working_hours = SelectMultipleField("Рабочие часы",
                                        choices=[('08:00-14:00', '08:00-14:00'), ('14:00-20:00', '14:00-20:00'),
                                                 ('20:00-02:00', '20:00-02:00'), ('02:00-08:00', '02:00-08:00')])
    submit = SubmitField('Добавить')
    update = SubmitField('Обновить')
