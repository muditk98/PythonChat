import tkinter as tk
import os
import client2

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
def loginPage():
	global uname_entry,label,uname_label,login_button,tag
	label = tk.Label(window, text='Login Page', font=LARGE_FONT)
	label.grid(row=0,sticky='')
	uname_label=tk.Label(window, text="Username").grid(row=1,column=0)
	uname_entry = tk.Entry(window)
	uname_entry.grid(row=1, column=1)
	login_button= tk.Button(window, text='Login')
	login_button.grid(row=2, column=0)
	tag=1
	login_button.bind("<Button-1>",destroyloginPage)

def destroyloginPage(event):
	global window,USERNAME,uname_entry,tag
	print('dgfdhdhd')
	if(tag==1):
		USERNAME=uname_entry.get()
	data = pickle.dumps({'type': 'login', 'author': USERNAME})
	client2.transmitbytes(client2.guisock_out, data)
	# print(pickle.loads(receivebytes(s)))
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

def destroyconnectedPage(event):
	global window,v,recv_type,recv_type_name,recv_entry, destination, USERNAME
	recv_type=v.get()
	recv_type_name=recv_entry.get()
	print(str(recv_type)+"::::"+recv_type_name)

	if recv_type == 1:
		destination['user'] = [recv_type_name]
	else:
		destination['group'] = [recv_type_name]
		data = pickle.dumps({'type': 'joingroup', 'data': recv_type_name, 'author': USERNAME})
		client2.transmitbytes(client2.guisock_out, data)


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
	my_pane_frame2 = tk.Frame(window,relief='raised',bd=2)
	my_pane_frame2.pack(fill=tk.BOTH)
	my_paned_window_2 = tk.PanedWindow(my_pane_frame2,bd=2)
	my_paned_window_2.pack(fill=tk.BOTH, expand=2)
	left_pane_text2 = tk.Entry(my_paned_window_2,font=15)
	def sendText(event):
		global left_pane_text2,left_pane_text
		message = left_pane_text2.get()
		data = pickle.dumps({'type': 'text', 'data': message, 'author': USERNAME, 'destination': destination})
		client2.transmitbytes(client2.guisock_out, data)
		left_pane_text.insert(tk.END,USERNAME+": "+left_pane_text2.get()+"\n")
		left_pane_text2.delete(0,tk.END)

	left_pane_text2.bind("<Return>",sendText)
	my_paned_window_2.add(left_pane_text2)
	back_button=tk.Button(window, text='Back')
	tag=2
	back_button.bind("<Button-1>",destroyloginPage)
	my_paned_window_2.add(back_button)

  
if __name__ == '__main__':
	pid = os.fork()
	if pid == 0:
		client2.chat_client()
	else:
		loginPage()
		window.mainloop()		