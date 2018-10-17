import pickle
import socket
import sys
import select

RECV_BUFFER = 2048
guisock_in, guisock_out = socket.socketpair()
guisock_in.settimeout(1)
guisock_out.settimeout(1)

def frame_message(type, data, author, destination):
	return {'type': type, 'data': data, 'author': author, 'destination': destination}

def frame_text_message(data, destination):
	return frame_message('text', data, USERNAME, destination)

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

HOST = 'localhost'
port = 2021
addr = (HOST, port)

def message(uname):
	data = dict()
	data['type'] = 'text'
	data['destination'] = dict()
	data['destination']['user'], data['destination']['group'], data['data'] = sys.stdin.readline().split('#')
	data['destination']['user'] = data['destination']['user'].split(',')
	data['destination']['group'] = data['destination']['group'].split(',')
	data['author'] = uname
	return pickle.dumps(data)

def chat_client():
	# if(len(sys.argv) < 3) :
	#     print 'Usage : python chat_client.py hostname port'
	#     sys.exit()

	# host = sys.argv[1]
	# port = int(sys.argv[2])
	 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	 
	# connect to remote host
	try :
		s.connect(addr)
	except :
		print('Unable to connect')
		sys.exit()
	 
	# uname = input('Enter uname: ')
	# data = pickle.dumps({'type': 'login', 'author': uname})
	transmitbytes(s, data)
	print(pickle.loads(receivebytes(s)))
	print('Connected to remote host. You can start sending messages')

	sys.stdout.write(f'[{uname}] ')
	sys.stdout.flush()

	 
	while True:
		socket_list = [guisock_in, s]
		
		# Get the list sockets which are readable
		ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
		
		for sock in ready_to_read:             
			if sock == s:
				# incoming message from remote server, s
				data = receivebytes(sock)
				if not data :
					print('\nDisconnected from chat server')
					sys.exit()
				else :
					#print data
					data = pickle.loads(data)
					# DISPLAY IN THE RECEIVE FRAME
					# sys.stdout.write(data['data'])
					# sys.stdout.write(f'[{uname}] ')
					# sys.stdout.flush()     
			
			else :
				# user entered a message
				data = receivebytes(sock)
				if not data :
					print('Warning: Empty data')
					sys.exit()
				else :
					#print data
					transmitbytes(s, data)
					data = pickle.loads(data)
					# DISPLAY IN THE RECIEVE FRAME

					# sys.stdout.write(data['data'])
					# sys.stdout.write(f'[{uname}] ')
					# sys.stdout.flush()     

if __name__ == "__main__":

	sys.exit(chat_client())

