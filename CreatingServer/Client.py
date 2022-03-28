import socket
import hashlib




def CheckPassword(a):

    if len(a) < 8:
        return 'Пароль должен быть больше 8 символов'

    if a.islower() or a.isupper():
        return 'Пароль должен иметь прописные и заглавные буквы'

    if a.isdigit() or a.isalpha():
        return 'Пароль должен иметь как цифры, так и буквы'

    def check(s): return not all(
        'a' <= x <= 'z' or '0' <= x <= '9' or 'а' <= x <= 'я' or 'А' <= x <= 'Я' or 'A' <= x <= 'Z' for x in s)

    if check(a) == True:
        return 'Неразрешенные символы'

    return True


def SighIn():
    login = input('Login:')
    password = input('Password:')

    

    while True:
        """sock = socket.socket()
        #sock.bind(("127.0.0.1",9999))
        sock.connect(('127.0.0.1', 9090))"""

        hash = hashlib.md5(password.encode()+login.encode()).hexdigest()
        #print(hash)

        text = '-l ' + login + " " + hash
        

        sock.send(text.encode())

        data = sock.recv(1024)

        print(data)
        break


def SighUp():

    

    name = input("Name:")
    while True:

        login = input('New login:')

        text = 'r ' + login
        #print(text)
        sock.send(text.encode())

        data = sock.recv(1024)
        if data.decode() == "Such a login already exists":
            print(data.decode())
        elif data.decode() == "Success":
            break
    while True:
        password = input("Password:")
        if CheckPassword(password) == True:
            break
        else:
            print(CheckPassword(password))

    text = "-r " + login + " " + name + " " + password
    #print(text)
    sock.send(text.encode())

    data = sock.recv(1024)
    print(data.decode())





def InputCommands():
    while True:
        text = input("$:")
        if(text != ''):
            commands = text.split()

            if commands[0] == "-r":
                SighUp()
            elif commands[0] == "-l":
                SighIn()
            elif commands[0] == '-h':
                print("-r: Sigh up\n-l: Sigh in\n-h: Get help")
            elif commands[0] == '-q':
                sock.send("-q".encode())
                sock.close()
                break
            else:
                print("Unknown command")



sock = socket.socket()
# sock.bind(("127.0.0.1",9999))
sock.connect(('127.0.0.1', 9090))



InputCommands()
