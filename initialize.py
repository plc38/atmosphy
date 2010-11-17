import sqlite3
import os


def atmosStoragePath(filename=''):
    return os.path.expanduser(os.path.join('~/.atmosphy', filename))

#def getDBPath():
#	return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf.d','pycaskur.db3')

class modelDB():

    def __init__(self, dbPath=atmosStoragePath('atmosphy.db3')):
    
    	"""Initialize the database with a model at the dbPath location"""
    	
    	if not os.path.exists(os.path.dirname(dbPath)): os.system('mkdir %s' %os.path.dirname(dbPath))
    	
    	initModelsTable = """CREATE TABLE models(model_name STRING, 
    										model_description STRING,
    										model_url STRING,
    										model_ondisk BOOL DEFAULT 0)"""
    	
    	if os.path.exists(dbPath): print "Warning: Overwriting database"

    	connection = sqlite3.connect(os.path.abspath(dbPath))
    	connection.execute(initModelsTable)
    	connection.close()
    	
    	return None
    	
    	



    # todo - need to make something that installs the conf.d file
    
    
    
										
#def initModelDB(modelName, columnNames , dbPath='~/.pycaskur/modeldb.db3'):
#	"""initialize a model table with filenames, this will be called when downloading a new model"""
#	initModelTable = "CREATE TABLE %s(filename,%s)"""%','.join(columnNames)"





