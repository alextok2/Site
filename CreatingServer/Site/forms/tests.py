from unicodedata import category
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, RadioField, Label
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired



class SubmitForm(FlaskForm):
    submit = SubmitField("Принять")


class GenerateTestForm(FlaskForm):
    questions = Label('', text="2")
    radio_fields = RadioField('', choices=[])
    

    def __init__(self, choices):
        super().__init__()
        # self.questions.label = label1
        # self.questions.label = text
        # self.radio_fields.label = text
        self.radio_fields.choices = choices
        



    # login = StringField('Логин', validators=[DataRequired()])
    # password = StringField('Пароль', validators=[DataRequired()])
    # content = TextAreaField("Содержание")
    # role = SelectField("Роль", choices=[1, 2, 3], coerce=int)
    # submit = SubmitField('Следующий вопрос')
    # submit = SubmitField('Предыдущий вопрос')
