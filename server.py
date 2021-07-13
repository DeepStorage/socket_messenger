import threading
import socket
import time
from datetime import datetime


print('\n'*50)

host = "127.0.0.1"
port = 10001
max_conn = 30
buffer = 1024

while 1:
	try:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind((host, port))
		server.listen(max_conn)
		break
	except Exception as e:
		print(e)
		time.sleep(0.1)

clients = []
nicknames = []

def broadcast(message):
	for client in clients:
		try:
			if client.getpeername()[0] in vip_list:
				message = b"[VIP] " + message
			client.send(message)
			print("\n" + message.decode('utf8'))
		except Exception as e:
			print(e)

def handle(client):
	while 1:
		try:
			message = client.recv(buffer)
			broadcast(message)
		except:
			index = clients.index(client)
			try:
				clients.remove(client)
			except:
				pass
			client.close()
			nickname = nicknames[index]
			broadcast(f"{nickname} left the chat.".encode('utf8'))
			print(f"\n{nickname} left the chat.")
			try:
				nicknames.remove(nickname)
			except:
				pass
			break

def receive():
	while 1:
		try:
			client, address = server.accept()
			print(f"\nConnected with {str(address)}")

			client.send('NICK'.encode('utf8'))
			nickname = client.recv(buffer).decode('utf8')
			nicknames.append(nickname)
			clients.append(client)

			print(f"{address}'s nickname is {nickname}\n")
			broadcast(f"{nickname} joined the chat.".encode('utf8'))
			client.send("Connected to server!".encode('utf8'))

			thread = threading.Thread(target=handle, args=(client,))
			thread.start()
		except:
			pass




# ---------------------------------------------
# ADMIN FUNCTIONS
# ---------------------------------------------
def kick(user):
	if user in nicknames:
		i = nicknames.index(user)
		clients[i].close()

		broadcast(f"\n[SERVER] User {user} kicked out!\n".encode('utf8'))
	else:
		print("\nUser not online")

def users():
	if len(nicknames) == 0:
		print("\nNo users online!")
	else:
		print()
		for i in range(0, len(nicknames)):
			print(nicknames[i])
		print()

ban_list = []
vip_list = []

with open("ban_list.txt", "r") as file_ban_list:
	ban_list = file_ban_list.readlines()

with open("vip_list.txt", "r") as file_vip_list:
	vip_list = file_vip_list.readlines()


def ban(user):
	i = nicknames.index(user)
	ban_u = clients[i]

	b_host, b_port = ban_u.getpeername()

	user = b_host

	global ban_list
	ban_list.append(user)

	with open("ban_list.txt", "w") as f:
		for i in ban_list:
			f.write(i)

def unban(user):
	global ban_list
	if user in ban_list:
		ban_list.remove(user)
	else:
		print("\nUser not banned")

	with open("ban_list.txt", "w") as f:
		for i in ban_list:
			f.write(i)

def vip(user):
	broadcast(f'{user} is now VIP'.encode('utf8'))

	i = nicknames.index(user)
	ban_u = clients[i]

	b_host, b_port = ban_u.getpeername()

	user = b_host

	global vip_list
	vip_list.append(user)

	with open("vip_list.txt", "w") as f:
		for i in vip_list:
			f.write(i)

def remove_vip(user):
	broadcast(f'{user} is no longer VIP'.encode('utf8'))

	i = nicknames.index(user)
	ban_u = clients[i]

	b_host, b_port = ban_u.getpeername()

	user = b_host

	global vip_list
	if user in vip_list:
		vip_list.remove(user)
	else:
		print("\nUser is not vip")

	with open("vip_list.txt", "w") as f:
		for i in vip_list:
			f.write(i)



def kick_banned():
	while 1:
		for i in ban_list:
			for c in clients:
				h, p = c.getpeername()
				if h == i:
					c.send(b'You are banned at this server!')
					kick(nicknames[clients.index(c)])
		time.sleep(0.2)


# ---------------------------------------------
# END
# ---------------------------------------------


def admin():
	global server
	command_list = """
	/kick [nickname]	kick user
	/ban [nickname]		ban user
	/unban [hostname]	unban user
	/ban_list		show list of banned users
	/vip [nickname]		just vip
	/remove_vip [nickname]
	/vip_list		show vip list
	/users		show online users
	/close 		close server
	/cls 		clear
	"""
	print("Type '/help' for command list")

	admin_input = ""
	while 1:
		while len(admin_input) == 0:
			admin_input = input()

		if admin_input[0] == '/':

			if admin_input == '/help':
				print("\n" + command_list)

			if '/kick ' in admin_input:
				admin_input = admin_input.replace("/kick ", "")
				kick(admin_input)

			elif admin_input == "/users":
				users()

			elif '/ban ' in admin_input:
				admin_input = admin_input.replace('/ban ', '')
				print(f"\nbanning {admin_input}")
				ban(admin_input)

			elif '/unban ' in admin_input:
				admin_input = admin_input.replace('/unban ', '')
				print(f"\nunbanning {admin_input}")
				unban(admin_input)

			elif '/ban_list' in admin_input:
				print()
				for i in ban_list:
					print(i)
				print()

			elif '/vip ' in admin_input:
				admin_input = admin_input.replace('/vip ', '')
				vip(admin_input)

			elif '/remove_vip ' in admin_input:
				admin_input = admin_input.replace('/remove_vip ', '')
				remove_vip(admin_input)

			elif '/vip_list' in admin_input:
				print()
				for i in vip_list:
					print(i)
				print(i)

			elif '/close' in admin_input:
				server.close()
				while len(clients) > 0:
					for client in clients:
						client.close()
				print("\n\nServer closed!")

			elif '/cls' in admin_input:
				print('\n'*50)


			else:
				print("\nCommand not found. Type '/help' for command list")

		else:
			message = ("[ADMIN] " + admin_input + "\n").encode('utf8')
			broadcast(message)

		admin_input = ""


print(f"""
Server is UP!

Listening on:
	hostname: {host}
	port: {port}

config:
	buffer: {buffer}
	max_conn: {max_conn}

Listening...

	""")

admin_thread = threading.Thread(target=admin)
admin_thread.start()

ban_thread = threading.Thread(target=kick_banned)
ban_thread.start()

receive()

print("Script ended!")