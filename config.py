import os
import pickle

_config_database = None

def _get_database_file_name():
    home = os.path.expanduser("~")
    db_file_name = home + "/.remoter"
    return db_file_name

def _load_database():
    global _config_database

    if _config_database is not None:
        return _config_database

    # try:
    #     fp = open(_get_database_file_name())
    # except:
    #     fp = None
    #
    # if fp is not None:
    #     _config_database = pickle.load(fp)
    # else:
    #     _config_database = {}

    _config_database = {}

    # fp.close()
    return _config_database

def _load_config_entry(name):
    db = _load_database()
#    print "loading keys for %s" % name
    try:
        return db[name]
    except:
#        print "no keys found for %s" % name
        return {}

def _write_config_entry(name, obj):
    db = _load_database()
    db[name] = obj

    fp = open(_get_database_file_name(), 'w')
    pickle.dump(db, fp)
    fp.close()


class ConfigDB:
    def __init__(self, config_db_key):
        self.__config_db_key = config_db_key
        self.__config_entry = _load_config_entry(self.__config_db_key)

    def get(self, name):
        return self.__config_entry[name]

    def set(self, name, obj):
        self.__config_entry[name] = obj
        _write_config_entry(self.__config_db_key, self.__config_entry)

    def keys(self):
        ret = []
        for f in self.__config_entry:
            ret.append(f)

        return ret

    def values(self):
        ret = []
        for f in self.keys():
            ret.append(self.get(f))

        return ret
