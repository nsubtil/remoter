import subprocess
import shlex
import ssh
import directorymonitor

_default_rsync_bin_path = '/usr/local/bin/rsync'
_default_rsync_options = '-Ccrlptv --exclude=/build*/ --exclude=/bin/ --include=.git --del'

def run_rsync(localpath, remote_config, main, output=None):
    sshconn = ssh.SSHConnectionDB().get(remote_config['remote_name'])

    cmdline = _default_rsync_bin_path

    # add ssh options
    cmdline += " -e '%s'" % sshconn.ssh_build_cmdline(bare=True)

    cmdline += " %s" % _default_rsync_options
    cmdline += " %s/" % localpath

    cmdline += " "
    if sshconn.user is not None:
        cmdline += "%s@" % sshconn.user

    cmdline += "%s:%s/" % (sshconn.host, remote_config['remote_root'])

    print "running [%s]" % cmdline

    args = shlex.split(cmdline)
    pipe = subprocess.Popen(args, stdout=output, stderr=output)
    pipe.communicate()

    return pipe.returncode
