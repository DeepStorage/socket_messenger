import threading
import socket

print('\n'*50)

nickname = input("Choose a nickname: ")


host = "127.0.0.1"
port = 10001
buffer = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive():
	while 1:
		try:
			message = client.recv(buffer).decode('utf8')
			if message == 'NICK':
				client.send(nickname.encode('utf8'))
			else:
				print(message)
		except Exception as e:
			print(e)
			client.close()
			break

def write():
	while 1:
		message = f"{nickname}: {input()}"
		client.send(message.encode('utf8'))


receive_thread = threading.Thread(target=receive,)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()