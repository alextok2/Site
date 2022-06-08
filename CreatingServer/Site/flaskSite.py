# from crypt import methods
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

from forms.tests import GenerateTestForm, SubmitForm
from forms.roles import RoleForm


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

    if request.method == 'POST':
        score = 0
        for i in range(len(answers_json['answers'])):

            if int(request.form.get(f'answer{i}')) == answers_json['right_answers'][i]:
                score += 1

        results = round(score / test.max_score * 100)

        result = Result()
        result.test_id = id_test
        result.user_id = current_user.id
        result.score = results
        result.date = datetime.datetime.utcnow()

        db_sess.add(result)
        db_sess.commit()

    return render_template('poll.html', test=test.name,
                           answers=answers_json['answers'], questions=questions, length=len(answers_json['answers']))


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

    y_key = []
    x_best = []

    if len(y) == 1:
        y_key.append(y[0])

    else:
        for i in range(len(y)-1):
            if y[i] != y[i+1]:
                y_key.append(y[i])

    old_i = None
    k = -1
    for i in y_key:

        for j in range(len(y)):
            if y[j] == i:
                print(y[j])
                if old_i != i:
                    print(y[j])
                    x_best.append(x[j])
                    old_i = i
                    k += 1

                if x_best[k] < x[j]:
                    x_best[k] = x[j]

    print(y_key, x_best)

    fig1 = px.bar(y=y_key, x=x_best, labels=dict(
        x="Оценки", y="Дисциплины", color="Place"))

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
    if current_user.role != Role.Admin.value:
        return "У вас недостаточно прав."
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
    # app.jinja_env.globals.update(clever_function=clever_function)
    app.jinja_env.globals.update(clear_token=clear_token)
    app.run(debug=True, host=app.config["ADDRESS"], port=app.config['PORT'])
