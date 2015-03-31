import watchdog
import watchdog.events
import watchdog.observers

class EventListener(watchdog.events.FileSystemEventHandler):
    '''Event listener skeleton, meant to be derived from'''
    def on_any_event(self, event):
        pass

class DirectoryMonitor:
    '''Simple class to monitor changes starting at a given root directory in the filesystem.'''

    def __init__(self, rootpath, eventhandler):
        self.__rootpath = rootpath
        self.__observer = watchdog.observers.Observer()
        self.__eventHandler = eventhandler

    def run(self):
        print "monitoring %s" % self.__rootpath
        self.__observer.schedule(self.__eventHandler, self.__rootpath, recursive=True)
        self.__observer.start()

    def stop(self):
        self.__observer.stop()

    def join(self):
        self.__observer.join()
