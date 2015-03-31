#!/usr/bin/env python2.7

import os
import socket
import argparse
import json
import sys
import struct

default_socket_address = os.path.expanduser('~') + "/.remoter-socket"

working_directory = os.getcwd()
print working_directory

parser = argparse.ArgumentParser(description="Launch remote builds")
parser.add_argument('-t', '--target', metavar='target_host', nargs=1, required=True, help="Target host to run build on")
parser.add_argument('command', nargs=argparse.REMAINDER, help="Build commands to run on remote host")

args = parser.parse_args()
remote_command = ['run-remote-command', {'target_host': args.target[0], 'local_path': working_directory, 'command': ' '.join(args.command)}]

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(default_socket_address)
f = s.makefile()

command = json.dumps(remote_command)

f.write(command + "\n")
f.flush()

data = s.recv(1)
while data != '':
    #if struct.unpack("!B", data[0]) == 0xff:
    if data == '\xff':
        l = f.readline()
        js = json.loads(l)
        if js[0] == 'returncode':
            sys.exit(js[1])
        else:
            print "=== remoter client: invalid json received [%s]" % js
            sys.exit(255)

    sys.stdout.write(data)
    sys.stdout.flush()
    data = s.recv(1)
