#!/usr/bin/env python
import socket
import sys
import argparse
import json
import getpass
import ssl

parser = argparse.ArgumentParser()
parser.add_argument('host', action='store', help='Server host',
    default='127.0.0.1')
parser.add_argument('port', action='store', help='Server port',
    default='9555')
parser.add_argument('ca', action='store', help='CA certificate',
    default='stunnel/easyrsa/pki/ca.crt')
parser.add_argument('cert', action='store', help='Client certificate',
    default='stunnel/easyrsa/pki/issues/client-cert.crt')
parser.add_argument('key', action='store', help='Client certificate key',
    default='stunnel/easyrsa/pki/private/client-cert.key')


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




