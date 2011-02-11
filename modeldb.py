import sqlite3
import initialize
import bz2
import cPickle as pickle
def convertBzipPickle(bzipPickle):
    "Converts a bzipped pickle into a normal object again"
    return pickle.loads(bz2.decompress(bzipPickle))

class modelDBException(Exception):
    pass

class database:
    def __init__(self):
        self.filename = '~/.atmosphy/atmosphy.db3'
        return sqlite3.connect(os.path.expanduser(self.filename),
                               detect_types=sqlite3.PARSE_DECLTYPES)

"""
def initModelTable(modelName, clobber=False):
    "Creating Model Table"

    conn = getModelDBConnection()
    if len(conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND    name='%s'" 
        % (modelName,)).fetchall()) == 1:
        if clobber:
            conn.execute('DROP TABLE `%s`' % (modelName,))
        else:
            raise modelDBException("Model %s already exists in database"
                                 % (modelName,))

    initModelTable = """CREATE TABLE `%s` (    id INTEGER PRIMARY KEY,
                                            teff DOUBLE,
                                            logg DOUBLE,
                                            feh DOUBLE,
                                            k DOUBLE,
                                            alpha DOUBLE,
                                            lh DOUBLE,
                                            pradk DOUBLE,
                                            deck BZPKL)""" % modelName
    conn.execute(initModelTable)
    conn.commit()
    conn.close()
"""

def insertModelData(conn, modelName, dataTuple):
    "Insert data into the model database"
    dataTuple[-1] = sqlite3.Binary(dataTuple[-1])
    conn.execute(
        'insert into `%s` (teff, logg, feh, k, alpha, lh, pradk, deck)'
        'values (?,?,?,?,?,?,?,?)' % (modelName,), tuple(dataTuple))

sqlite3.register_converter("BZPKL", convertBzipPickle)