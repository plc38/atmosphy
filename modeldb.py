import sqlite3
#import initialize
import bz2
import cPickle as pickle
import os
import numpy as np
def convertBzipPickle(bzipPickle):
    "Converts a bzipped pickle into a normal object again"
    return pickle.loads(bz2.decompress(bzipPickle))

def convertNPMemmap(NPMemmap):
    return np.fromstring(NPMemmap)
    
    
class modelDBException(Exception):
    pass

def getModelDBConn(dbPath = '~/.atmosphy/atmosphy.db3'):
    dbPath = os.path.expanduser(dbPath)
    return sqlite3.connect(dbPath,
                               detect_types=sqlite3.PARSE_DECLTYPES)
"""
def initModelTable(modelName, clobber=False):
    "Creating Model Table"

	conn = getModelDBConnection()
	if len(conn.execute(
		"SELECT name FROM sqlite_master WHERE type='table' AND	name='%s'" 
		% (modelName,)).fetchall()) == 1:
		if clobber:
			conn.execute('DROP TABLE `%s`' % (modelName,))
		else:
			raise modelExistsException("Model %s already exists in database"
								 % (modelName,))

    initModelTable = ""CREATE TABLE `%s` (    id INTEGER PRIMARY KEY,
                                            teff DOUBLE,
                                            logg DOUBLE,
                                            feh DOUBLE,
                                            k DOUBLE,
                                            alpha DOUBLE,
                                            lh DOUBLE,
                                            pradk DOUBLE,
                                            deck BZPKL)"" % modelName
    conn.execute(initModelTable)
    conn.commit()
    conn.close()
"""

def insertModelData(conn, modelName, dataTuple):
    "Insert data into the model database"
    dataTuple[-1] = sqlite3.Binary(dataTuple[-1].tostring())
    #dataTuple[-1] = sqlite3.Binary(bz2.compress(pickle.dumps(dataTuple[-1])))
    
    conn.execute(
        'insert into MODELS (model_id, teff, logg, feh, alpha, k, lh, deck)'
        'values (?, ?, ?, ?, ?, ?, ?, ?)', tuple(dataTuple))

sqlite3.register_converter("NP_MEMMAP", convertNPMemmap)
sqlite3.register_converter("BZPKL", convertBzipPickle)
