from xml.etree.ElementTree import fromstring, ElementTree
import xml.etree.ElementTree as ET
import ipaddress
import time
import socket
import struct
import re
from  contextlib import closing
import hashlib







def IP2Int(ip):
	return( struct.unpack("!I", socket.inet_aton(str(ip)))[0])

def Int2IP(ipnum):
    return ipaddress.ip_address(int(ipnum))
    
def CreateServer():
	
	
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	port = FindTag("port")
	address = FindTag("ip")

	sock.bind((str(address), int(port)))
	sock.listen(1)
	
	
	conn, addr = sock.accept()
	print("connected:", addr)



	
	while True: 
		if addr[1] == "":
			conn, addr = sock.accept()

		
		data = conn.recv(1024)
		
		



		if data.decode() =="":
			continue
		
		print("connected:", addr)

		
		text = data.decode()
		print(text)
		commands = text.split()
		if commands[0] == '-l':
			if SearchLoginsAndPasswords(commands[1], commands[2]) == True:
				print('Welcome', commands[1])
				print(IsAdmin(commands[1]))
				if IsAdmin(commands[1]) == True:
					print("You're admin")
				else:
					print("You're not admin")
				conn.send(("Welcome").encode())
		elif commands[0] == 'r':
			if ThereIsLoginsDublicats(commands[1]) == False:
				conn.send(("Such a login already exists").encode())
			elif ThereIsLoginsDublicats(commands[1]) == True:
				conn.send(("Success").encode())
		elif commands[0] == '-r':
			CreateNewPerson(commands[1], commands[2], commands[3])
			conn.send(("Success").encode())
			
			
		elif commands[0] == '-q':
			try:
				with closing(sock):
					sock.shutdown(socket.SHUT_RDWR)
					conn.close()
			except OSError:
				pass
			break
		commands = [] 
				


		
		#print(data.decode("utf-8") ,type(data))
		
		'''if(data.upper().decode("utf-8") =="1"):
			conn.send(FindTag("time").encode())
		elif(data.upper().decode("utf-8") =="2"):
			conn.send(str(FindTag("ip")).encode())
		elif(data.upper().decode("utf-8") =="3"):
			conn.send("Goodbye".encode()) 
			
			try:
				with closing(sock):
					sock.shutdown(socket.SHUT_RDWR)
					conn.close()
			except OSError:
				pass
			break

		else:
			conn.send("There's no such commands".encode())
		time.sleep(0.1)
		'''
		

def CloseSoccet(open_socket, open_connection):
	try:
		with closing(open_socket):
			open_socket.shutdown(socket.SHUT_RDWR)
			open_connection.close()
	except OSError:
		pass



def RewriteTag(search_tag, new_value):
	for child in root:
		if child.tag == search_tag:
			if child.tag == "ip":
				child.text=str(IP2Int(new_value))
			else:
				child.text=new_value
			tree.write("/root/ProjectsVC/CreatingServer/text.xml")

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
	
	tree.write("/root/ProjectsVC/CreatingServer/text.xml")

def FindTag(search_tag):
	for child in root:
	    if root.tag == search_tag:
	        print(child.tag)
	    else:
	        if child.tag==search_tag:
	            if child.tag == "ip":
	              try:
	                ip = Int2IP(int(child.text.split()[0]))	                
	                return ip
	              except ValueError:
	                print('Incorrect IP address')
	              except IndexError:
	                print('Bad input string')
	            elif child.tag == "date":
	              try:
	                valid_date = time.strptime(child.text, '%d.%m.%Y')
	                return(child.text)
	              except ValueError:
	                print('Invalid date!')
	            else:
	                return(child.text)

def IsAdmin(search_login):
	for person in root.iter('person'): 
		login = person.find('login').text
		
		if login == search_login:
			
			if person.find('admin').text == 'true':
				return True
			else:
				return False
	return None



def SearchLoginsAndPasswords(search_login, search_hash):
	for person in root.iter('person'): 

		login = person.find('login').text
		if login == search_login:
		
			login = login.encode()
			password = (person.find('password').text).encode()
			hash = hashlib.md5(password+login).hexdigest()

			if search_hash == hash:
				return True
	return False





def InputCommands():
	text= input("$:")
	if(text!=''):
		commands = text.split()
	
		if commands[0] == "-f":
			print(FindTag(commands[1]))
		elif commands[0] == "-s":
			CreateServer()
		elif commands[0] == '-l':
			print(CheckLoginsDublicats(commands[1]))
		elif commands[0] == '-c':
			CreateNewPerson(commands[1],commands[2],commands[3])
		elif commands[0] == '-w':
			RewriteTag(commands[1],commands[2])
		elif commands[0] == '-h':
			print("-f <tag>: Find tag\n-s: Create server\n-w <tag> <new value>: Rewrite new value in tag\n-h: Get help")
		else:
			print("Unknown command")
	InputCommands()



InputCommands()