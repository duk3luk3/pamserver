#!/usr/bin/env python
try:
  import pam
except ImportError:
  import simplepam as pam

try:
  import SocketServer
except ImportError:
  import socketserver as SocketServer

try:
  import ConfigParser
except ImportError:
  import configparser as ConfigParser

import json
import argparse
import socket

import sys
import logging
import logging.handlers
import os

import util

log_formatter = logging.Formatter('pamserver %(levelname)s: %(message)s')
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
logger = logging.getLogger('pamserver')
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)


#logging.basicConfig(format='pamserver %(levelname)s: %(message)s',
#    level=logger.DEBUG)

class RequestHandler(SocketServer.BaseRequestHandler):
  def reply(self, data, status=200, message='OK'):
    sock = self.request
    obj = {
        'status_code': status,
        'reason': message,
        'data': data
        }
    sock.sendall(bytes(json.dumps(obj), 'utf-8'))

  def handle(self):
    logger.debug("Received connection.")
    while True:
      try:
        r = self.request.recv(1024)
        if len(r) == 0:
          logger.debug("Client quit")
          break
        data = json.loads(str(r, 'utf-8'))
      except ValueError:
        self.reply({}, status=400, message='JSON Parse error')

      if 'username' in data:
        if 'password' in data:
          username = data['username']
          password = data['password']
          service = data.get('service', 'login')
          if pam.authenticate(username, password, service=service):
            self.reply({}, status=200, message='Authentication successful.')
          else:
            self.reply({}, status=401, message='Authentication failed.')
        else:
          self.reply({}, status=400, message='Password is missing.')
      else:
        self.reply({}, status=400, message='Username is missing.')

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', dest='configfile', action='store',
      default='/etc/pamserver/config',
      help='The config file')
  parser.add_argument('--sock', dest='sockfile', action='store',
      help='Pass to customize the sockfile location')
  parser.add_argument('--pid', dest='pidfile', action='store',
      help='Pass to customize the pidfile location')
  parser.add_argument('--syslog', dest='syslog', action='store_true',
      default=None,
      help='Pass to turn on logger to syslog')
  parser.add_argument('--no-syslog', dest='syslog', action='store_false',
      default=None,
      help='Pass to turn off logger to syslog')
  parser.add_argument('--no-pid', dest='pidfile', action='store_false',
      help='Pass to turn off pidfile')

  args = parser.parse_args()
  config = {}
  try:
    with open(args.configfile) as f:
      try:
        config = json.load(f)
      except ValueError:
        logger.error("Config file {} does not contain a valid JSON object".
            format(args.configfile))
  except:
    logger.warn("Could not open config file: {}".format(sys.exc_info()[1]))

  if args.sockfile == None:
    logger.debug("Checking sockfile config")
    args.sockfile = config.get('sockfile', None) or \
        '/var/run/pamserver/pamserver.s'
  if args.syslog == None:
    args.syslog = config.get('syslog', None) or False
  if args.pidfile == None:
    logger.debug("Checking pidfile config")
    args.pidfile = config.get('pidfile', None) or \
        '/var/run/pamserver/pamserver.pid'

  if args.syslog:
    syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
    syslog_handler.setFormatter(log_formatter)
    logger.addHandler(syslog_handler)

  args.sockfile = os.path.abspath(args.sockfile)

  if not os.path.exists(os.path.dirname(args.sockfile)):
    logger.warn("Sockfile dir does not exist, trying to create")
    try:
      util.mkdir_recursive(os.path.dirname(args.sockfile))
    except FileExistsError:
      logger.error("There is a file in the way: {}".format(sys.exc_info()[1]))
      logger.error("Cannot continue without sockfile, aborting")
      return
    except:
      logger.error("Could not create sockfile {}: {}".format(args.sockfile, sys.exc_info()[1]))
      logger.error("Cannot continue without sockfile, aborting")
      return


  if args.pidfile:
    args.pidfile = os.path.abspath(args.pidfile)
    if not os.path.exists(os.path.dirname(args.pidfile)):
      logger.warn("Sockfile dir does not exist, trying to create")
      try:
        util.mkdir_recursive(os.path.dirname(args.pidfile))
      except FileExistsError:
        logger.error("There is a file in the way: {}".format(sys.exc_info()[1]))
        logger.error("Cannot continue without pidfile, aborting")
        return
      except:
        logger.error("Could not create pidfile: {}".format(sys.exc_info()[1]))
        logger.error("Cannot continue without pidfile, aborting")
        return

  if args.pidfile:
    pid = os.getpid()
    with open(args.pidfile, 'w') as pidfile:
      pidfile.write(str(pid))

  logger.info("Starting server.")

  try:
    server = SocketServer.UnixStreamServer(args.sockfile, RequestHandler)
    server.serve_forever()
  except KeyboardInterrupt:
    logger.info("Interrupted by SIGKILL, closing.")

  logger.info("Server stopped, cleaning up.")

  try:
    os.remove(args.sockfile)
  except:
    logger.warn("Could not remove sockfile: {}".format(sys.exc_info()[1]))

  if args.pidfile:
    try:
      os.remove(args.pidfile)
    except:
      logger.warn("Could not remove pidfile: {}".format(sys.exc_info()[1]))

  logger.info("pamserver shut down.")

if __name__ == "__main__":
  run()
