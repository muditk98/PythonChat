import sys
import socket
import select
import pickle
import pymongo


'''

11 -> 
12 -> user already logged in
13 -> Group does not exist

'''

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client['chatap']

HOST = '' 
PORT = 2021
if len(sys.argv) > 2:
	HOST = sys.argv[1]
	port = int(sys.argv[2])

SOCKET_LIST = []
RECV_BUFFER = 2048 

username_sock_table = dict()
backlogCollection = db['backlog']
userCollection = db['user']
groupCollection = db['group']
groupUserCollection = db['group_user']


def number_to_base(n, b):
	if n == 0:
		return [0]
	digits = []
	while n:
		digits.append(int(n % b))
		n //= b
	return digits[::-1]

def transmitbytes(sockfd, data):
	n = len(data)
	msglen = number_to_base(n, 256)
	while len(msglen) < 3:
		msglen = [0] + msglen
	if len(msglen) > 3:
		print("Size of data is more than maximum size of 16 MB", file=sys.stderr)
		return -1
	payload = bytes(msglen)+bytes(data)
	sockfd.sendall(payload)

def receivebytes(sockfd):
	msglenbytes = list(sockfd.recv(3))
	msglen = 0
	for i in msglenbytes:
		msglen = msglen*256 + i
	chunks = []
	bytes_recd = 0
	while bytes_recd < msglen:
		chunk = sockfd.recv(min(msglen - bytes_recd, RECV_BUFFER))
		if chunk == b'':
			return b''
		chunks.append(chunk)
		bytes_recd = bytes_recd + len(chunk)
	return b''.join(chunks)

def process_message(sock, data):
	if data['type'] == 'login':
		name = data['author']
		row = userCollection.find_one({'name': name})
		if not row:
			# transmitbytes(sock, bytes({'type': 'error', 'data': 11}))
			userCollection.insert_one({'name': name})
			# transmitbytes(sock, pickle.dumps({'type': 'text', 'data': 'New user registered', 'author': 'server'}))
		if name not in username_sock_table:
			username_sock_table[name] = sock
			transmitbytes(sock, pickle.dumps({'type': 'text', 'data': 'Logged in successfully', 'author': 'server'}))
			old_messages = list(backlogCollection.find({'name': name}))
			print('Old message count: ', len(old_messages))
			backlogCollection.delete_many({'name': name})
			for message in old_messages:
				send_message([name], pickle.loads(message['data']))

		else:
			transmitbytes(sock, pickle.dumps({'type': 'error', 'data': '12', 'author': 'server'}))
	elif username_sock_table[data['author']] != sock:
		return

	elif data['type'] == 'joingroup':
		row = groupCollection.find_one({'name': data['data']})
		if not row:
			row = groupCollection.insert_one({'name': data['data']})
		row = groupUserCollection.find_one({'group_name': data['data'], 'user_name': data['author']})
		if not row:
			groupUserCollection.insert_one({'group_name': data['data'], 'user_name': data['author']})

	elif data['type'] == 'leavegroup':
		group_row = groupCollection.find_one({'name': data['data']})
		if group_row:
			count = groupUserCollection.delete_many({'group_name': group_row['name'], 'user_name': data['author']})
			print('Delete leave count:', count)
		else:
			transmitbytes(sock, pickle.dumps({'type': 'error', 'data': '13', 'author': 'server'}))

	else:
		print('Here for text')
		userlist = data['destination'].get('user', [])
		userlist.append(data['author'])
		if 'group' in data['destination']:
			for group in data['destination']['group']:
				temp = groupUserCollection.find({'group_name': group}, {'user_name': 1})
				for row in temp:
					userlist.append(row['user_name'])
		userlist = list(set(userlist))
		print('user list: ', userlist)
		send_message(userlist, data)

def send_message(userlist, data):
	pickled_data = pickle.dumps(data)
	for user in userlist:
		if user in username_sock_table:
			transmitbytes(username_sock_table[user], pickled_data)
		elif userCollection.find_one({'name': user}):
			backlogCollection.insert_one({'name': user, 'data': pickled_data})


def chat_server():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((HOST, PORT))
	server_socket.listen(10)
	SOCKET_LIST.append(server_socket)
	print("Chat server started on port " + str(PORT))

	while True:
		ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
		for sock in ready_to_read:
			if sock == server_socket: 
				sockfd, addr = server_socket.accept()
				SOCKET_LIST.append(sockfd)
				print(f"Client {addr} connected")
				# broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
			else:
				try:
					data = receivebytes(sock)
					if data:
						data = pickle.loads(data)
						print(data)
						process_message(sock, data)
					else:
						if sock in SOCKET_LIST:
							SOCKET_LIST.remove(sock)

							delete_list = []
							for user in username_sock_table:
								if sock == username_sock_table[user]:
									delete_list.append(user)
							for user in delete_list:
								username_sock_table.pop(user)

						print(f"Client {sock.getpeername()} is offline") 

				except Exception as e:
					print('Error: ', e)
					# broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
					continue
	server_socket.close()


def broadcast (server_socket, sock, message):
	for socket in SOCKET_LIST:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				socket.close()
				if socket in SOCKET_LIST:
					SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":

	sys.exit(chat_server())