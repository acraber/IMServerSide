from socket import *
from threading import Thread
import sys
import time

BUFSIZE = 1024
EXIT = '[Q]'


class Server:
    connections = []
    user_list = {}

    def __init__(self, ip='127.0.0.1', port=49000):
        """
        Create a server that accepts connections and spawns connection threads
        :param ip: defaults to localhost or pass in your IP
        :param port: defaults to 49000 or pass in your desired port
        """
        addr = (ip, port)
        self.sock = socket(AF_INET, SOCK_STREAM)
        # Allow the reuse of the addr in the event an application was just using it
        # self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind(addr)
        self.sock.listen(5)
        print(f'Server Started and Listening on: {addr}')

    def start(self):
        """Start running the server"""
        while True:
            conn, addr = self.sock.accept()
            # Receive screen name from client
            name = conn.recv(BUFSIZE).decode()
            print(f'   {name.capitalize()} - {addr} connected')

            # Create a thread for new client, daemon true, and start thread calling run()
            client_handler = ConnectionHandler(conn, addr, name)
            client_handler.start()
            Server.connections.append(conn)


class ConnectionHandler(Thread):
    """A sub class of Thread to start a thread to handle
    client connection with the server known as a session"""
    def __init__(self, client_conn, client_addr, screen_name):
        super().__init__(daemon=True)
        self.conn = client_conn
        self.name = screen_name
        self.addr = client_addr
        # Daemon allows abrupt exiting
        # self.daemon = True

    def run(self):
        """Start processing chat session in a thread"""
        # userlist dict - usernames: client_sock_conn
        Server.user_list[self.name] = self.conn
        ConnectionHandler.send_to_all(f'{self.name} joined chat...')
        while True:
            try:
                recv_msg = self.conn.recv(BUFSIZE)
                msg = recv_msg.decode()
            except:
                recv_msg = None
                print(f'**Invalid data from {self.name} {self.addr}')

            if not recv_msg or EXIT in msg:
                print(f'\t{self.name.capitalize()} - {self.addr} disconnected')
                Server.connections.remove(self.conn)
                Server.user_list.pop(self.name)
                self.conn.close()
                self.send_to_all(f'{self.name} left chat...')
                break

            if '@' == msg[0]:
                # Private message one user
                send_name = msg[1:].split(' ')[0]
                Server.user_list[send_name].send(f'{self.name}: {msg}'.encode())
            else:
                # Message everyone
                ConnectionHandler.send_to_all(f'{self.name}: {msg}')

    @staticmethod
    def send_to_all(message):
        for conn in Server.connections:
            conn.send(message.encode())


# Main logic - Create server object and start the server
server = Server()
server.start()
