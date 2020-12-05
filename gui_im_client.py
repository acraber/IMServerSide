from tkinter import *
from tkinter import messagebox
from socket import *
from threading import Thread

sock = socket()
messages = []
EXIT = '[Q]'


def window_closing():
    """Handles the closing of the program safely without leaving any open connections."""
    if sock:
        disconnect()
    win.quit()


def ip_entry_event_handler(event):
    """Handles the key entries from the IP address entry widget."""
    valid_keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', '\b', '']
    if event.char in valid_keys:
        if event.char == '' or event.char == '\b':
            ip_entry_txt.set(ip_entry_txt.get()[:-1])
            return "break"
        else:
            ip_entry_txt.set(ip_entry_txt.get() + event.char)
            return "break"
    else:
        return "break"



def disconnect():
    """Disconnects from the server and updates the GUI"""
    try:
        sock.send(EXIT.encode())
    except:
        pass
    finally:
        sock.close()
        print('Socket Disconnected')
    connect_button['bg'] = 'SystemButtonFace'
    connect_button['text'] = 'Connect'
    connect_button['command'] = connect
    message_listbox.grid_forget()
    win.geometry("330x75")
    message_txt.set('')


def receive_msg():
    """Receives a message from the server and displays it to the listbox."""
    global sock
    print('Thread started')
    msg = ''
    while True:
        try:
            msg = sock.recv(1024)

        except OSError:
            msg = None
            break
        if not msg:
            disconnect()
            break
        update_listbox(msg.decode())





def send_message():
    """Sends the message to the server."""
    global sock
    msg = message_txt.get()
    if msg == EXIT:
        disconnect()
    elif msg != '':
        try:
            sock.send(msg.encode())
        except OSError:
            disconnect()
    message_txt.set('')


def update_listbox(msg):
    """TODO: DO DOCSTRING"""
    message_listbox.delete(0, len(messages))
    messages.append(msg)
    count = 0
    for message in messages:
        message_listbox.insert(count, message)
        count += 1
        message_listbox.yview_scroll(count, UNITS)


def connect():
    """Connects the client to the server and changes the GUI"""
    global ip_entry_txt, scrname_entry_txt, sock
    if len(ip_entry_txt.get()) >= 6 and len(scrname_entry_txt.get()) > 0:
        screen_name = scrname_entry_txt.get()
        HOST = ip_entry_txt.get()
        ADDR = (HOST, 49000)
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.connect(ADDR)
            print(f'Connected to {ADDR}')
            sock.send(screen_name.encode())
        except:
            sock.close()
            sock = None
        else:
            receive_msg_thread = Thread(target=receive_msg, daemon=True)
            receive_msg_thread.start()
        win.geometry("330x510")
        connect_button['text'] = 'Disconnect'
        connect_button['bg'] = 'light blue'
        connect_button['command'] = disconnect
        message_listbox.grid(row=3, column=0, columnspan=2, ipady=120, sticky=N+S+E+W)
        print(f'connected to {HOST}')
    else:
        messagebox.showinfo(title='Error', message='You must enter an IP address with at least 6 digits and '
                                                   'a username.')




win = Tk()
win.geometry("330x75")
win.title("Instant Messenger")

message_txt = StringVar()
ip_entry_txt = StringVar()
scrname_entry_txt = StringVar()
ip_entry_txt.set('127.0.0.1')

ip_label = Label(win, text="Server IP")
ip_label.grid(row=0, column=0, padx=(0, 25), sticky=W)
ip_entry = Entry(win, textvariable=ip_entry_txt, justify=LEFT, width=35)
ip_entry.grid(row=0, column=1, sticky=E)
ip_entry.bind('<Key>', ip_entry_event_handler)

scrname_label = Label(win, text="Screen Name")
scrname_label.grid(row=1, column=0, padx=(0, 25), sticky=W)
scrname_entry = Entry(win, textvariable=scrname_entry_txt, justify=LEFT, width=35)
scrname_entry.grid(row=1, column=1, sticky=E)

connect_button = Button(text="Connect", width=45, command=connect)
connect_button.grid(row=2, column=0, columnspan=2)

scrollbar = Scrollbar(win)
message_listbox = Listbox(win, borderwidth=5, highlightcolor='light blue', yscrollcommand=scrollbar.set)
scrollbar.config(command=message_listbox.yview)


message_entry = Entry(win, textvariable=message_txt)
message_entry.grid(row=4, column=0, columnspan=2, ipadx=80, sticky=W)

send_btn = Button(win, text="Send", command=send_message)
send_btn.grid(row=4, column=1, ipadx=15, sticky=E)

win.protocol("WM_DELETE_WINDOW", window_closing)
win.mainloop()