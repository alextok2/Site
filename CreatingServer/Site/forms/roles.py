from unicodedata import category
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired

class RoleForm(FlaskForm):
    # title = StringField('Заголовок', validators=[DataRequired()])
    # content = TextAreaField("Содержание")
    role = SelectField("Роль", choices=[1,2,3], coerce=int)
    # submit = SubmitField('Применить')