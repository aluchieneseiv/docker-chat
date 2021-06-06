import socket
from msgpack import packb, unpackb
from getpass import getpass
from threading import Thread
import hashlib

HOST = 'localhost'
PORT = 2000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send(obj):
    sock.sendall(packb(obj))

def recv():
    return unpackb(sock.recv(1024))

def password_hash(s):
    return hashlib.sha256(s.encode()).digest()

def process_message(msg):
    #print(repr(msg))

    if msg['type'] == 'drop':
        print(f'You have been kicked for reason: {msg["reason"]}')
    elif msg['type'] == 'info':
        print(msg['content'])
    elif msg['type'] == 'chat':
        print(f'{msg["sender"]}: {msg["content"]}')
    elif msg['type'] == 'dm':
        print(f'{msg["sender"]} -> {msg["content"]}')

def handle_messages():
    while True:
        process_message(recv())

if __name__ == '__main__':
    username = input('username: ')
    password = getpass('password: ')

    with sock as s:
        s.connect((HOST, PORT))

        send({
            'type': 'auth',
            'username': username,
            'password': password_hash(password)
        })

        t = Thread(target=handle_messages)
        t.daemon = True
        t.start()

        while True:
            line = input()

            if line.startswith('/'):
                split = line.split(' ')
                cmd = split[0]
                if cmd == '/dm':
                    send({
                        'type': 'dm',
                        'target': split[1],
                        'content': ' '.join(split[2:])
                    })
                    continue

                if cmd == '/exit':
                    break

                print('Unknown command')
                continue

            send({
                'type': 'chat',
                'content': line
            })