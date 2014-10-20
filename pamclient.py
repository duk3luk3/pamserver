#!/usr/bin/env python
import socket
import sys
import argparse
import json
import getpass
from six.moves import input
from six import PY3

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

    b = json.dumps(data)
    if PY3:
      b = bytes(jo, 'utf-8')
    sock.sendall(b)

    r = sock.recv(1024)
    if PY3:
      r = str(r, 'utf-8')
    print(json.loads(r))
except KeyboardInterrupt:
  print("Bye!")

sock.close()




