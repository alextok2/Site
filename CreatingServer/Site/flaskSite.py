from flask import Flask, render_template, request, jsonify, redirect
import xml.etree.ElementTree as ET
import hashlib

app = Flask(__name__)

tree = ET.parse('CreatingServer/text.xml')
root = tree.getroot()

def SearchLoginsAndPasswords(search_login, search_hash):
    for person in root.iter('person'): 
        login = person.find('login').text

        if login == search_login:
            
            hash = (person.find('password').text)

            if search_hash == hash:
                return True
    return False

def ThereIsLoginsDublicats(newLogin):
	for person in root.iter('person'): 
		if person.find('login').text == newLogin:
			return True
	return False

def CreateNewPerson(newLogin, newName, newPassword):
	a = root.find('people') 
	person = ET.SubElement(a, 'person') 
	login = ET.SubElement(person, 'login') 
	password = ET.SubElement(person, 'password')
	admin = ET.SubElement(person, 'admin')
	person.set('name',newName) 
	login.text = newLogin 
	password.text = newPassword 
	admin.text = "false"
	
	tree.write("CreatingServer/text.xml")


@app.route("/index")
@app.route("/")
def index():
    if checkAuth(request):
        return render_template('index.html', title="ржач")
    else:
        return redirect("auth")

@app.route("/auth")
def auth():
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
    if SearchLoginsAndPasswords(login,passwordHash) == True:
        return True
    
    return False

if __name__ == '__main__':
    app.run(debug=True, host="localhost")#, ssl_context=('CreatingServer/Site/resourses/cert.pem', 'CreatingServer/Site/resourses/key.pem'))
    
