import SocketServer
import os
import rsync
import json
import struct

default_socket_address = os.path.expanduser('~') + "/.remoter-socket"

class Handler(SocketServer.StreamRequestHandler):
    def __send_end_marker(self, returncode):
        self.wfile.write(struct.pack("!B", 0xff))
        self.wfile.write(json.dumps(['returncode', returncode]) + "\n")

    def __handle_remote_command(self, command_args):
        main = self.server.getmain()

        try:
            target_host = command_args['target_host']
            local_path = command_args['local_path']
            command = command_args['command']
        except:
            self.wfile.write("=== remoter: protocol error: invalid arguments for run-remote-command\n")
            self.__send_end_marker(255)
            return

        # search through the list of projects trying to match any component of the local path
        project = None
        for p in main.project_db.values():
            if os.path.commonprefix([p.root + "/", local_path + "/"]) == p.root + "/":
                project = p
                break

        if project == None:
            self.wfile.write("=== remoter: could not find project for local path %s\n" % local_path)
            self.__send_end_marker(255)
            return

        remote = None
        for r in project.remotes:
            if r['remote_name'] == target_host:
                remote = r
                break

        if remote == None:
            self.wfile.write("=== remoter: could not find remote %s for project %s\n" % (target_host, project.name))
            self.__send_end_marker(255)
            return

        ssh = main.host_db.get(remote['remote_name'])
        if not ssh.is_connected():
            self.wfile.write('=== remoter: connecting to %s...\n' % remote['remote_name'])
            ssh.connect()

        self.wfile.write('=== remoter: synchronizing %s to %s:%s...\n' % (project.name, remote['remote_name'], remote['remote_root']))
        retcode = rsync.run_rsync(project.root, remote, main, output=self.wfile)
        if retcode != 0:
            self.wfile.write('=== remoter: synchronization error\n')
            self.__send_end_marker(retcode)
            return

        # translate the local path to remote
        remote_root = os.path.join(remote['remote_root'], os.path.relpath(local_path, project.root))

        cmdline = "cd %s && %s | sed -u 's#%s#%s#'" % (remote_root, command, remote['remote_root'], project.root)
        self.wfile.write('=== remoter: running command [%s] on host [%s]\n' % (cmdline, remote['remote_name']))

        try:
            ssh.run(cmdline, stdout=self.wfile)
            ssh.wait()
            self.__send_end_marker(ssh.pipe.returncode)
        except Exception as e:
            pass

    def handle(self):
        main = self.server.getmain()
        req = json.loads(self.rfile.readline())

        # json: [ 'command', { args dict } ]
        # valid commands:
        #  [ 'run-remote-command', {'local_path': local working directory for project,
        #                           'target_host': target remote host,
        #                           'command': command string to run } ]

        if req[0] == "run-remote-command":
            self.__handle_remote_command(req[1])
            return
        else:
            self.wfile.write("=== remoter: protocol error: invalid command\n")
            self.__send_end_marker(255)
            return

class RemoterServer(SocketServer.UnixStreamServer):
    daemon_threads = True

    def __init__(self, main):
        self.__main = main

        # make sure the socket doesn't exist
        try:
            os.unlink(default_socket_address)
        except OSError:
            if os.path.exists(default_socket_address):
                raise

        SocketServer.UnixStreamServer.__init__(self, default_socket_address, Handler)
        self.fd = self.fileno()

    def getmain(self):
        return self.__main
