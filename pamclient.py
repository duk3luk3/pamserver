#!/usr/bin/env python
import socket
import sys
import argparse
import json
import getpass

parser = argparse.ArgumentParser()
parser.add_argument('sock', action='store', help='the socket file')

args = parser.parse_args()
print(args)

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(args.sock)

try:
  while True:
    data = {}
    data['username'] = input("Enter name: ")
    data['password'] = getpass.getpass("Enter pass: ")
    sock.sendall(bytes(json.dumps(data), 'utf-8'))
    r = str(sock.recv(1024), 'utf-8')
    print(json.loads(r))
except KeyboardInterrupt:
  print("Bye!")

sock.close()




