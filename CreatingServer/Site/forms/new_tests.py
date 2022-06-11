from unicodedata import category
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, RadioField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewTestForm(FlaskForm):
    style = {'style': 'width:50%;'}
    name = StringField('Наименованние теста', validators=[
                       DataRequired()], render_kw=style)
    question = TextAreaField('Вопрос', validators=[
                             DataRequired()], render_kw=style)

    answer0 = StringField('Ответ 1', validators=[
                          DataRequired()], render_kw=style)
    answer1 = StringField('Ответ 2', validators=[
                          DataRequired()], render_kw=style)
    answer2 = StringField('Ответ 3', render_kw=style)
    answer3 = StringField('Ответ 4', render_kw=style)

    # create_new_answer = SubmitField("Создать новый ответ")
    previous = SubmitField('Предыдущий вопрос')
    submit = SubmitField('Завершить')
    next = SubmitField('Следующий')

    # option1 = BooleanField('label')
    # option2 = BooleanField('label')
    # option3 = BooleanField('label')
    # option4 = BooleanField('label')

    # def __init__(self, data):
    #     super().__init__()
    #     self.answer.data = data
