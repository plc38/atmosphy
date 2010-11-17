import sqlite3
import initialize

class modelDBException(Exception):
	pass

def getModelDBConnection():
	"returns a connection to the modelDB"
	return sqlite3.connect(initialize.atmosStoragePath('atmosphy.db3'))
	
def initModelTable(modelName, clobber=False):
	"Creating Model Table"

	conn = getModelDBConnection()
	if len(conn.execute(
		"SELECT name FROM sqlite_master WHERE type='table' AND	name='%s'" 
		% (modelName,)).fetchall()) == 1:
		if clobber:
			conn.execute('DROP TABLE %s' % (modelName,))
		else:
			raise modelDBException("Model table already exists")

	initModelTable = """CREATE TABLE %s(	id INTEGER PRIMARY KEY,
    										teff DOUBLE,
    										logg DOUBLE,
    										feh DOUBLE,
    										k DOUBLE,
    										alpha DOUBLE,
    										lh DOUBLE,
    										pradk DOUBLE,
    										deck BLOB)"""%modelName
	conn.execute(initModelTable)
	conn.commit()
	conn.close()
	
def insertModelData(conn, modelName, dataTuple):
	"Insert data into the model database"
	dataTuple[-1] = sqlite3.Binary(dataTuple[-1])
	conn.execute(
		'insert into %s(teff, logg, feh, k, alpha, lh, pradk, deck)'
		'values (?,?,?,?,?,?,?,?)' % (modelName,), tuple(dataTuple))
