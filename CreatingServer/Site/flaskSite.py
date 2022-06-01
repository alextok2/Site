import datetime
from re import A
from flask import Flask, make_response, render_template, request, jsonify, redirect, url_for
from functools import wraps
import jwt
import xml.etree.ElementTree as ET
import hashlib
import enum

from requests import session

from data import db_session
from data.users import User
from data.groups import Group
from data.results import Result
from data.sessions import Session
from data.tests import Test


class Role(enum.Enum):
    Student = 0
    Curator = 1
    Admin = 2



app = Flask(__name__)
app.config['SECRET_KEY'] = "8f42a73054b1749f8f58848be5e6502c"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        # token = None

        # if 'x-access-token' in request.headers:
        #     token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing'}), 403
            # return redirect("auth")

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            print(data["user_id"])
            with db_session.create_session() as db_sess:

                current_user = db_sess.query(User).filter(User.id==data["user_id"]).first()
        except:
            return jsonify({'message' : 'Token is invalid'}), 403
            # return redirect("auth")

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/poll")
@token_required
def Poll(current_user):
    

    
    # token = jwt.encode({'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    # eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTQwODQ3Njl9.gN6ZzBsF9GWlok5JRWakqjtSd890Ou2A-g-OyltyAM4
    # return jsonify({'token' : token.decode('UTF-8')})

    return render_template('poll.html', login=current_user.login)           


def SearchLoginsAndPasswords(search_login, search_hash):
    if search_login != None or search_hash != None:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login==search_login and User.password==search_hash).first()
        
        if user != None:
            # print(user.fio)
            return True
    return False


def ThereIsLoginsDublicats(newLogin):
    if newLogin != None:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login==newLogin).first()
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
        token = jwt.encode({'user_id' : user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180)}, app.config['SECRET_KEY'])
        user_session.token = token
        db_sess.add(user_session)
        db_sess.commit()
        
    


@app.route("/index")
@app.route("/")
def index():
    if checkAuth(request):
        return render_template('index.html', title="ржач")
    else:
        return redirect("auth")

@app.route("/auth")
def auth():
    # print(url_for('Register'))
    return render_template('auth.html')

@app.route("/register")
def Register():
    return render_template('register.html')




@app.route("/api/register", methods=['POST'])
def checkRegister():
    content = request.json
    login = content['login']
    password = content['passwordHash']
    name = content['name']
    
    CreateNewPerson(login, name, password)

    return "Success", 200


@app.route("/register/loginExists")
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

    
@app.route("/api/login", methods=['POST'])
def login():
    content = request.json

    #hash = hashlib.sha256(content['password']+content['login']).hexdigest()
    print(content['login'],content['passwordHash'])
    if SearchLoginsAndPasswords(content['login'],content['passwordHash']) == True:
        return "Success", 200
    
    return "Record not found", 400

@app.route("/example") 
def about():
    if checkAuth(request):
        return render_template('example.html')
    else:
        return redirect("auth")


def checkAuth(request):
    login = request.cookies.get('login')
    passwordHash = request.cookies.get('passwordHash')
    print(login, passwordHash)
    if SearchLoginsAndPasswords(login,passwordHash) == True:
        return True
    
    return False





if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    # user = User()
    # user.fio = "Максим Максимов Максимович"
    # user.login = 'maksim2004'
    # user.password = 'b8786cd8f23456e8b84788abd022f4ca'
    # user.role = Role.Student.value
    
    # with db_session.create_session() as db_sess:
    #     db_sess.add(user)
    #     db_sess.commit()
    
    # SearchLoginsAndPasswords1("maksim2004", 'b8786cd8f23456e8b84788abd022f4ca')
    
    app.run(debug=True, host="localhost")#, ssl_context=('CreatingServer/Site/resourses/cert.pem', 'CreatingServer/Site/resourses/key.pem'))
    
