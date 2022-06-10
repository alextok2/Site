# from crypt import methods
from multiprocessing.connection import answer_challenge
import re
from traceback import print_tb
from jinja2 import Template
from dataclasses import field
import datetime
from operator import length_hint
from re import A
from flask import Flask, make_response, render_template, request, jsonify, redirect, url_for, Response
from functools import wraps
import jwt
import xml.etree.ElementTree as ET
import hashlib
import enum
import json
from requests import session
import os
import pandas as pd
import plotly
import plotly.express as px


from sqlalchemy import true

from data import db_session
from data.users import User
from data.groups import Group
from data.results import Result
from data.sessions import Session
from data.tests import Test

from forms.tests import GenerateTestForm
from forms.roles import RoleForm
from forms.new_tests import NewTestForm


class Role(enum.Enum):
    Student = 0
    Curator = 1
    Admin = 2


roles = ["Студент", "Преподаватель", "Админ"]

file_path = os.path.abspath(os.getcwd())+"\db\blogs.sqlite"
print(file_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = "8f42a73054b1749f8f58848be5e6502c"
app.config['ADDRESS'] = "127.0.0.1"
app.config['PORT'] = "5000"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')

        if not token:
            # return jsonify({'message' : 'Token is missing'}), 403
            return redirect(url_for("auth"))

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])

            with db_session.create_session() as db_sess:

                current_user = db_sess.query(User).filter(
                    User.id == data["user_id"]).first()
        except:
            # return jsonify({'message' : 'Token is invalid'}), 403
            return redirect(url_for("auth"))

        return f(current_user, *args, **kwargs)

    return decorated


def clear_token():
    token = request.cookies.get('token')
    print(token)
    # print(current_user.fio)


def SearchLoginsAndPasswords(search_login, search_hash):
    if search_login != None or search_hash != None:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.login == search_login and User.password == search_hash).first()

        if user != None:
            # print(user.fio)
            return True
    return False


def ThereIsLoginsDublicats(newLogin):
    if newLogin != None:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == newLogin).first()
        if user != None:
            # print(user.fio)
            return True
    return False


def CreateNewPerson(new_login, new_fio, new_password):

    with db_session.create_session() as db_sess:
        user = User()
        user.fio = new_fio
        user.login = new_login
        user.password = new_password
        user.role = Role.Student.value
        db_sess.add(user)
        db_sess.commit()

        user_session = Session()
        user_session.user_id = user.id
        token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=180)}, app.config['SECRET_KEY'])
        user_session.token = token
        db_sess.add(user_session)
        db_sess.commit()


@app.route("/role")
@token_required
def role(current_user):
    db_sess = db_session.create_session()

    if current_user.role == Role.Admin.value:

        user = db_sess.query(User)
        return render_template('role.html', user=user, roles=roles)
    else:
        return "У вас недостаточно прав."

@app.route("/create_user")
@token_required
def create_user(current_user):
    if current_user.role != Role.Admin.value:
        return "У вас недостаточно прав."

    db_sess = db_session.create_session()
    user = db_sess.query(User).order_by(User.id.desc()).first()

    print(user.id)
    return redirect(url_for("edit_role", id=user.id))

@app.route("/role/<int:id>", methods=['GET', 'POST'])
@token_required
def edit_role(current_user, id):

    if current_user.role != Role.Admin.value:
        return "У вас недостаточно прав."

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    form = RoleForm(role=user.role)

    form.role.choices = [(i, roles[i]) for i in range(len(Role))]

    if form.validate_on_submit():

        user.role = form.role.data
        print(form.role.data)
        db_sess.commit()

        return redirect(url_for('role'))
    return render_template('edit_role.html', user=user, form=form)


@app.route("/poll")
@token_required
def all_poll(current_user):
    db_sess = db_session.create_session()
    tests = db_sess.query(Test).all()

    # print(tests.name)
    i = 1
    test_name = []
    for test in tests:

        test_name.append((i, test.name))
        i += 1

    return render_template('all_poll.html', test_name=test_name, length=len(test_name), url=url_for("all_poll"))


@app.route("/poll/<int:id_test>", methods=['GET', 'POST'])
@token_required
def poll(current_user, id_test):
    db_sess = db_session.create_session()
    test = db_sess.query(Test).filter(Test.id == id_test).first()

    questions = test.questions.split("%s")
    text = test.answers
    answers_json = json.loads(text)

    return render_template('poll.html', test=test.name,
                           answers=answers_json['answers'], questions=questions, length=len(answers_json['answers']), id=id_test)
    



@app.route("/edit_test/<int:test_id>/<int:question_id>", methods=['GET', 'POST'])
@token_required
def edit_test(current_user, test_id, question_id):
    if current_user.role != Role.Admin.value and current_user.role != Role.Curator.value:
        return "У вас недостаточно прав."
    
    form = NewTestForm()

    if request.method == "GET":
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.id == test_id).first()
        if test:
            form.name.data = test.name
            questions = test.questions.split("%s")
            form.question.data = questions[question_id]


            text = test.answers
            answers_json = json.loads(text)
            answers = []
            for answer in answers_json['answers']:
                answers.append(answer)
            
            right_answer = answers_json['right_answers'][question_id] - 1
            print(right_answer)

            try:
                form.answer0.data = answers[question_id][0]   
                form.answer1.data = answers[question_id][1]
                form.answer2.data = answers[question_id][2]
                form.answer3.data = answers[question_id][3]
            except IndexError:
                pass

            return render_template("edit_test.html", form=form, right_answer=right_answer)

    if form.validate_on_submit():
       
        db_sess = db_session.create_session()
        test = db_sess.query(Test).filter(Test.id == test_id).first()
        questions = test.questions.split("%s")

        questions[question_id] = form.question.data

        new_questions = ""
        for i in range(len(questions)):
            new_questions += questions[i] + "%s"

        test.questions = new_questions
        test.name = form.name.data
        db_sess.commit()




        text = test.answers
        answers_json = json.loads(text)
        print(answers_json)
        if form.answer0.data != '':
            answers_json['answers'][question_id][0] = form.answer0.data






        if form.answer3.data != '':
            if len(answers_json['answers'][question_id]) > 3:
                answers_json['answers'][question_id][3] = form.answer3.data
            else:
                answers_json['answers'][question_id].append(form.answer3.data)
        else:
            if len(answers_json['answers'][question_id]) > 3:
                del answers_json['answers'][question_id][3]

        if form.answer2.data != '':
            if len(answers_json['answers'][question_id]) > 2:
                answers_json['answers'][question_id][2] = form.answer2.data
            else:
                answers_json['answers'][question_id].append(form.answer2.data)
        else:
            if len(answers_json['answers'][question_id]) > 2:
                    del answers_json['answers'][question_id][2]

        if form.answer1.data != '':
            if len(answers_json['answers'][question_id]) > 1:
                answers_json['answers'][question_id][1] = form.answer1.data
            else:
                answers_json['answers'][question_id].append(form.answer1.data)
        else:
            if len(answers_json['answers'][question_id]) > 1:
                    del answers_json['answers'][question_id][1]
        
        option = request.form.get('answer')
        answers_json['right_answers'][question_id] = int(option)+1

        print(json.dumps(answers_json))
        test.answers = json.dumps(answers_json)
        db_sess.commit()
        
        if form.previous.data:
            if question_id > 0:
                return redirect(url_for('edit_test', test_id=test_id, question_id=question_id-1))
        if form.submit.data:
            print(form.data)
        if  form.next.data:
            return redirect(url_for('edit_test', test_id=test_id, question_id=question_id+1))

    return redirect(url_for('edit_test', test_id=test_id, question_id=question_id))

    
    



@app.route("/dashboard")
@token_required
def show_dashboard_result(current_user):

    db_sess = db_session.create_session()
    results = db_sess.query(Result).filter(
        Result.user_id == current_user.id).all()

    y = []
    x = []
    for result in results:
        x.append(result.score)
        y.append(db_sess.query(Test).filter(
            Test.id == result.test_id).first().name)

    if not x or not y:
        return redirect(url_for("all_poll"))

    x_best = []
    y_key = list(set(y))

    old_i = None
    k = -1
    for i in y_key:
        for j in range(len(y)):
            if y[j] == i:
                if old_i != i:
                    x_best.append(x[j])
                    old_i = i
                    k += 1

                if x_best[k] < x[j]:
                    x_best[k] = x[j]

    fig1 = px.bar(y=y_key, x=x_best, labels=dict(x="Оценки", y="Дисциплины", color="Place"))
    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("index2.html", graph1JSON=graph1JSON)


@app.route("/results")
@token_required
def show_result(current_user):
    db_sess = db_session.create_session()
    results = db_sess.query(Result).filter(
        Result.user_id == current_user.id).all()

    tests_name = []

    for result in results:
        tests_name.append(db_sess.query(Test).filter(
            Test.id == result.test_id).first().name)

    # for test in tests:
    #     for test1 in test:
    #         print(test1.name)

    return render_template("results.html", results=results, fio=current_user.fio, tests_name=tests_name)


@app.route("/index")
@app.route("/")
@token_required
def index(current_user):

    return render_template('index.html', login=current_user.login, path_role=url_for('role'), path_poll=url_for('all_poll'))

@app.route("/api/answer/<int:id_test>", methods=['POST'])
@token_required
def answer(current_user, id_test):

    content = request.json


    db_sess = db_session.create_session()
    test = db_sess.query(Test).filter(Test.id == id_test).first()

    text = test.answers
    answers_json = json.loads(text)


    score = 0
    for i in range(len(answers_json['answers'])):

        if (content['data'][i]+1) == answers_json['right_answers'][i]:
            score += 1
    
    results = { "result" : round(score / test.max_score * 100)}

    result = Result()
    result.test_id = id_test
    result.user_id = current_user.id
    result.score = results
    result.date = datetime.datetime.utcnow()

    db_sess.add(result)
    db_sess.commit()
    jsonify(results)

    return results


@app.route("/api/sigh_out")
@token_required
def sigh_out(current_user):
    print(current_user.id)
    db_sess = db_session.create_session()
    db_sess.query(Session).filter(Session.user_id == current_user.id).delete()
    db_sess.commit()
    res = make_response(redirect(url_for("auth")))
    res.set_cookie('token', "", expires=0)
    return res

@ app.route("/auth")
def auth():
    # print(url_for('Register'))
    return render_template('auth.html')


@ app.route("/register")
def Register():
    return render_template('register.html')


@ app.route("/api/register", methods=['POST'])
def checkRegister():
    content = request.json
    login = content['login']
    password = content['passwordHash']
    name = content['name']

    CreateNewPerson(login, name, password)

    return "Success", 200


@ app.route("/register/loginExists")
def checkLogin():
    login = request.args.get('login')
    print(login)
    if ThereIsLoginsDublicats(login):
        response = {
            "isValid": False
        }
    else:
        response = {
            "isValid": True
        }

    return jsonify(response)


@ app.route("/api/login", methods=['POST'])
def login():
    content = request.json
    login = request.get_json()['login']
    passwordHash = request.get_json()['passwordHash']
    print(login, passwordHash)

    if SearchLoginsAndPasswords(login, passwordHash) == True:

        with db_session.create_session() as db_sess:
            # Удаление старого токена

            user = db_sess.query(User).filter(
                User.login == login and User.password == passwordHash).first()
            user_session = db_sess.query(Session).filter(
                Session.user_id == user.id).delete()
            db_sess.commit()

            # Создание нового токена
            user_session = Session()
            user_session.user_id = user.id
            token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow(
            ) + datetime.timedelta(minutes=180)}, app.config['SECRET_KEY'])
            user_session.token = token
            db_sess.add(user_session)
            db_sess.commit()
        # token.decode('utf-8')
        data = '{"token":"' + token.decode('utf-8') + '"}'
        res = json.loads(data)

        return res, 200
    return "Record not found", 400


@app.route("/cabinet")
@token_required
def cabinet(current_user):
    return render_template('cabinet.html', fio=current_user.fio)


if __name__ == '__main__':
    db_session.global_init("blogs.sqlite")
    # user = User()
    # user.fio = "Максим Максимов Максимович"
    # user.login = 'maksim2004'
    # user.password = 'b8786cd8f23456e8b84788abd022f4ca'
    # user.role = Role.Student.value

    # with db_session.create_session() as db_sess:
    #     db_sess.add(user)
    #     db_sess.commit()
    # db_sess = db_session.create_session()

    # , ssl_context=('CreatingServer/Site/resourses/cert.pem', 'CreatingServer/Site/resourses/key.pem'))
    app.jinja_env.globals.update(clear_token=clear_token)
    app.run(debug=True, host=app.config["ADDRESS"], port=app.config['PORT'])
