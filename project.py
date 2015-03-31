import config
import directorymonitor
import rsync

# project = { 'name': 'nvbio-internal', 'root_path': '/Users/nsubtil/nvbio-internal',
#             'remotes': [ { 'ssh_connection': connobj,
#                            'remote_root': '/home/nsubtil/nvbio-internal' }, ... ]

class SynchronizedProjectDB (config.ConfigDB):
    __config_db_key = "synchronized_project_database"

    def __init__(self):
        config.ConfigDB.__init__(self, self.__config_db_key)

    def create_project(self, name, root):
        project = SynchronizedProject(name, root)
        self.set(name, project)
        return project

class _SynchronizedProjectMonitor (directorymonitor.EventListener):
    def __init__(self, project):
        self.__project = project

    def on_any_event(self, event):
        print "Update on project %s: event [%s] path [%s] is_directory [%s]" % (self.__project.name, event.event_type, event.src_path, event.is_directory)
        self.__project.main.update_queue.put(self.__project.name)

class SynchronizedProject:
    def __init__(self, name, root):
        self.__config = config

        self.name = name
        self.root = root
        self.remotes = []

        self.__file_event_handler = _SynchronizedProjectMonitor(self)
        self.__monitor = directorymonitor.DirectoryMonitor(self.root, self.__file_event_handler)

    def __getstate__(self):
        return {'name': self.name, 'root': self.root, 'remotes': self.remotes}

    def __setstate__(self, state):
        self.__init__(state['name'], state['root'], state['remotes'])

    def add_remote_build(self, remote_name, remote_root, auto_update=True):
        remote = {'remote_name': remote_name, 'remote_root': remote_root, 'auto_update': auto_update}
        print "remote build for %s at %s:%s" % (self.name, remote['remote_name'], remote['remote_root'])
        # the magic of python pass-by-object-reference makes this work
        self.remotes.append(remote)
        SynchronizedProjectDB().set(self.name, self)

    def update_remotes(self, main):
        print "updating project %s" % self.name
        for r in self.remotes:
            if r['auto_update']:
                print "--> remote %s" % r
                rsync.run_rsync(self.root, r, main)

    def start_monitor(self, main):
        self.main = main
        self.__monitor.run()

    def stop_monitor(self):
        self.__monitor.stop()

    def sync_monitor(self):
        self.__monitor.join()

