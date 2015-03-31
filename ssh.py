import subprocess
import config
import shlex

_default_ssh_bin_path = "/usr/local/bin/ssh"
_default_ssh_options = {
    'ClearAllForwardings': 'yes',
    'Compression': 'yes',
    'ControlPath': '~/.ssh/__remoter_%h.%p.%r',
    'ControlPersist': '3600',
    'ForwardX11': 'no',
    'NumberOfPasswordPrompts': '0',
    #'RequestTTY' : 'force',
}


class SSHConnectionDB (config.ConfigDB):
    __config_db_key = "remote_host_database"

    def __init__(self):
        config.ConfigDB.__init__(self, self.__config_db_key)

    def create_connection(self, name, host, port=None, user=None):
        conn = SSHConnection(name, host, port, user)
        self.set(name, conn)
        return conn

class SSHConnection:
    def __init__(self, name, host, port, user):
        self.__ssh_bin_path = _default_ssh_bin_path
        self.__ssh_options = _default_ssh_options

        self.name = name
        self.host = host
        self.port = port
        self.user = user

        self.last_output = None
        self.last_exit_code = None

    def __getstate__(self):
        return { 'name': self.name, 'host': self.host, 'port': self.port, 'user': self.user}

    def __setstate__(self, state):
        self.__init__(state['name'], state['host'], state['port'], state['user'])

    def ssh_build_cmdline(self, remote_command=None, bare=False):
        cmdline = self.__ssh_bin_path

        # add all our default ssh options
        for key in self.__ssh_options:
            cmdline += " -o %s=%s" % (key, self.__ssh_options[key])

        # user name
        if self.user is not None:
            cmdline += " -l %s" % self.user

        # port
        if self.port is not None:
            cmdline += " -p %s" % self.port

        # host name
        if not bare:
            cmdline += " %s" % self.host

        if not bare and remote_command is not None:
            cmdline += " %s" % remote_command

        return cmdline

    def is_connected(self):
        cmdline = self.ssh_build_cmdline("-O check")

        try:
            ret = subprocess.check_call(cmdline, shell=True)
            return True
        except:
            return False

    def connect(self):
        cmdline = self.ssh_build_cmdline("-M -N -f")
        ret = subprocess.check_call(cmdline, shell=True)

    def run(self, command, stdout=subprocess.PIPE):
        cmdline = self.ssh_build_cmdline(command)
        print "launching [%s]" % cmdline

        args = shlex.split(cmdline)
        self.pipe = subprocess.Popen(args, bufsize=0, stdout=stdout, stderr=stdout)

    def poll(self):
        return self.pipe.poll()

    def wait(self):
        return self.pipe.communicate()
