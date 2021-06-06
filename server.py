import socket
from threading import Thread
from msgpack import packb, unpackb
from typing import *

HOST = '0.0.0.0'
PORT = 2000

class Client:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def send(self, obj):
        self.conn.sendall(packb(obj))

    def recv(self):
        data = self.conn.recv(1024)
        if data:
            return unpackb(data)
        return None

clients: List[Client] = []

def find_client(username):
    for client in clients:
        if client.username == username:
            return client

    return None

def authenticate(username, hash):
    # placeholder
    return True

def broadcast(obj):
    for client in clients:
        client.send(obj)

def process_message(client, msg):
    # waiting for python3 match
    if msg['type'] == 'chat':
        broadcast({
            'type': 'chat',
            'sender': client.username,
            'content': msg['content']
        })
    elif msg['type'] == 'dm':
        target = find_client(msg['target'])
        if not target:
            client.send({
                'type': 'error',
                'content': f'No client with username {msg["target"]}'
            })
            return

        target.send({
            'type': 'dm',
            'sender': client.username,
            'content': msg['content']
        })

def handle_client(cl):
    with cl.conn:
        data = cl.recv()
        if data['type'] != 'auth':
            print(f'Client did not send auth, dropping: {cl.addr}')
            cl.send({
                'type': 'drop',
                'reason': 'No authentication given'
            })
            return
        
        cl.username = data['username']
        print(f'Client connected: {cl.addr}/{repr(cl.username)}')

        if not authenticate(cl.username, data['password']):
            print(f'Client dropped for bad auth: {cl.addr}/{repr(cl.username)}')
            cl.send({
                'type': 'drop',
                'reason': 'Authentication error'
            })
            return

        cl.send({
            'type': 'info',
            'content': 'Welcome to the server!'
        })
        
        try:
            while cl.conn:
                data = cl.recv()
                if not data:
                    raise IOError()

                process_message(cl, data)
        except IOError:
            print(f'Client disconnected: {cl.addr}/{repr(cl.username)}')

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sck:
        sck.bind((HOST, PORT))
        sck.listen()

        while True:
            conn, addr = sck.accept()
            c = Client(conn, addr)
            #print(f'Accepted {c.addr}')
            clients.append(c)
            Thread(target=handle_client, args=(c,)).start()
