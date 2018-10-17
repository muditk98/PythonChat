import pickle
import socket
import sys
import select
import time

RECV_BUFFER = 2048

HOST = 'localhost'
port = 2021
if len(sys.argv) > 2:
	HOST = sys.argv[1]
	port = int(sys.argv[2])

addr = (HOST, port)
guisock_in, guisock_out = socket.socketpair()
guisock_in.settimeout(1)
guisock_out.settimeout(1)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

# connect to remote host
try :
	s.connect(addr)
except :
	print('Unable to connect')
	sys.exit()
socket_list = [guisock_in, s]

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


def communicate():
	# Get the list sockets which are readable
	ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [], 0)
	
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
				return data
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

# def chat_client():
	# if(len(sys.argv) < 3) :
	#     print 'Usage : python chat_client.py hostname port'
	#     sys.exit()

	# host = sys.argv[1]
	# port = int(sys.argv[2])
	# uname = input('Enter uname: ')
	# data = pickle.dumps({'type': 'login', 'author': uname})
	# transmitbytes(s, data)
	# print(pickle.loads(receivebytes(s)))
	# print('Connected to remote host. You can start sending messages')

	# sys.stdout.write(f'[{uname}] ')
	# sys.stdout.flush()

import tkinter as tk
import os

window = tk.Tk()
window.geometry("500x500")
window.resizable(0, 0)
LARGE_FONT=("Verdana", 12)
label=tk.Label()
uname_label=tk.Label()
uname_entry=tk.Entry()
login_button=tk.Button()
recv_label=tk.Label()
recv_entry=tk.Entry()
recv_opt_rbt1=tk.Radiobutton()
recv_opt_rbt2=tk.Radiobutton()
#connect_button=tk.Button()
USERNAME=''
recv_type=0
recv_type_name=''
destination = dict()

tag=0
def loginPage(error = None):
	global uname_entry,label,uname_label,login_button,tag
	label = tk.Label(window, text='Login Page', font=LARGE_FONT)
	label.grid(row=0,sticky='')
	uname_label=tk.Label(window, text="Username").grid(row=1,column=0)
	uname_entry = tk.Entry(window)
	uname_entry.grid(row=1, column=1)
	login_button= tk.Button(window, text='Login')
	login_button.grid(row=2, column=0)
	tag=1
	if error:
		label2 = tk.Label(window, text='User is already logged in', font=LARGE_FONT).grid(row=3)
		error = None
	login_button.bind("<Button-1>",destroyloginPage)
	uname_entry.bind("<Return>",destroyloginPage)

def destroyloginPage(event):
	global window,USERNAME,uname_entry,tag
	print('dgfdhdhd')
	if(tag==1):
		USERNAME=uname_entry.get()
		data = pickle.dumps({'type': 'login', 'author': USERNAME})
		transmitbytes(s, data)
		data = pickle.loads(receivebytes(s))
		print(data)
		if data['type'] == 'error':
			loginPage()
			return
		# communicate()
	# print('Connected to remote host. You can start sending messages')
	print(USERNAME+" kkkk")
	window.destroy()
	window=tk.Tk()
	window.geometry("500x500")
	window.resizable(0, 0)
	connectedPage()
	#label.grid_forget()
	#uname_entry.grid_forget()
	#login_button.grid_forget()
	

def connectedPage():
	global window,recv_entry,recv_label,recv_opt_rbt1,recv_opt_rbt2,connect_button,v
	v=tk.IntVar(window)
	label = tk.Label(window, text='Welcome '+ USERNAME, font=LARGE_FONT)
	label.grid(row=0)
	recv_label=tk.Label(window, text="Enter reciever name").grid(row=1,column=0)
	recv_entry=tk.Entry(window)
	recv_entry.grid(row=1,column=1)
	recv_opt_rbt1=tk.Radiobutton(window,text="User", padx=20, variable=v, value=1).grid(row=2, column=0)
	recv_opt_rbt2=tk.Radiobutton(window,text="Group", padx=20, variable=v, value=2).grid(row=2, column=1)
	connect_button = tk.Button(window, text='connect')
	connect_button.grid(row=3, column=0)
	connect_button.bind("<Button-1>",destroyconnectedPage)
	# --
	label2 =tk.Label(window, text='Leave Group', font=LARGE_FONT).grid(row=4)
	leave_group_label=tk.Label(window, text="Enter group name")
	leave_group_label.grid(row=5,column=0)
	leave_group_entry=tk.Entry(window)
	leave_group_entry.grid(row=5,column=1)
	leave_group_button=tk.Button(window, text='Leave group')
	leave_group_button.grid(row=5,column=2)
	def leaveGroup(event):

		left_group_label=tk.Label(window, text="Left "+leave_group_entry.get()+" group")
		left_group_label.grid(row=6,column=0)
		data = pickle.dumps({'type': 'leavegroup', 'data': leave_group_entry.get(), 'author': USERNAME})
		transmitbytes(s, data)
		def deleteLabel():
			left_group_label.grid_forget()

		left_group_label.after(1500,deleteLabel)
	leave_group_button.bind("<Button-1>",leaveGroup)
	leave_group_entry.bind("<Return>",leaveGroup)

def destroyconnectedPage(event):
	global window,v,recv_type,recv_type_name,recv_entry, destination, USERNAME
	recv_type=v.get()
	recv_type_name=recv_entry.get()
	print(str(recv_type)+"::::"+recv_type_name)

	if recv_type == 1:
		destination['user'] = [recv_type_name]
		destination.pop('group', 0)
	else:
		destination['group'] = [recv_type_name]
		destination.pop('user', 0)
		data = pickle.dumps({'type': 'joingroup', 'data': recv_type_name, 'author': USERNAME})
		transmitbytes(s, data)

	# communicate()

	window.destroy()
	window=tk.Tk()
	window.geometry("500x500")
	window.resizable(0, 0)
	chatPage()

def chatPage():

	global window,v,recv_type,recv_type_name,recv_entry,label,back_button,left_pane_text,left_pane_text2,USERNAME,recv_entry,uname_entry,tag,destination
	temp=''
	if(recv_type==1):
		temp='User'
	elif(recv_type==2):
		temp='Group'
	label = tk.Label(window, text='Connected to '+temp+' '+recv_type_name, font=LARGE_FONT).pack()    # making the chat window where messages will appear.
	my_pane_frame1 = tk.Frame(window,relief='raised',bd=2)
	my_pane_frame1.pack(fill=tk.BOTH)
	scrollbar1 = tk.Scrollbar(my_pane_frame1)
	scrollbar1.pack(side = tk.RIGHT, fill = tk.Y )
	my_paned_window_1 = tk.PanedWindow(my_pane_frame1,bd=2)
	my_paned_window_1.pack(fill=tk.BOTH, expand=2)
	left_pane_text = tk.Text(my_paned_window_1, height=15, width=15,font=15, yscrollcommand=scrollbar1.set)
	my_paned_window_1.add(left_pane_text)
	scrollbar1.config( command =left_pane_text.yview)
	print("aaaaaa")
	def recv_text():
		data = communicate()
		# print("here")
		if data:
			if data['type'] == 'text':
				left_pane_text.insert(tk.END, data['author'] + ': ' + data['data'] + '\n')
			elif data['type'] == 'error':
				left_pane_text.insert(tk.END, data['author'] + ': ' + 'error: ' + data['data'] + '\n')
				time.sleep(1)
				sys.exit()

		left_pane_text.after(100, recv_text)
	my_pane_frame2 = tk.Frame(window,relief='raised',bd=2)
	my_pane_frame2.pack(fill=tk.BOTH)
	my_paned_window_2 = tk.PanedWindow(my_pane_frame2,bd=2)
	my_paned_window_2.pack(fill=tk.BOTH, expand=2)
	left_pane_text2 = tk.Entry(my_paned_window_2,font=15)
	# left_pane_text.after(100, recv_text)


	def sendText(event):
		global left_pane_text2,left_pane_text
		message = left_pane_text2.get()
		data = pickle.dumps({'type': 'text', 'data': message, 'author': USERNAME, 'destination': destination})
		transmitbytes(guisock_out, data)
		# communicate()
		# left_pane_text.insert(tk.END,USERNAME+": "+left_pane_text2.get()+"\n")
		left_pane_text2.delete(0,tk.END)

	left_pane_text2.bind("<Return>",sendText)
	my_paned_window_2.add(left_pane_text2)
	back_button=tk.Button(window, text='Back')
	tag=2
	back_button.bind("<Button-1>",destroyloginPage)
	my_paned_window_2.add(back_button)
	left_pane_text.after(100, recv_text)
	# root.after
  
if __name__ == '__main__':
	loginPage()
	window.mainloop()		

