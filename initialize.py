import sqlite3



def initDB(dbPath='~/.pycaskur/modeldb.db3'):
	"""Initialize the database with a model at the dbPath location"""
	
	dbPath = os.path.abspath(dbPath)
	
	initModelsTable = """CREATE TABLE models(model_name STRING, 
										model_description STRING,
										model_url STRING,
										model_ondisk BOOL DEFAULT 0)"""
	
	if os.path.exists(dbPath): print "Warning: Overwriting database"
	
	sqlite3.connect(os.path.abspath(dbPath))
	sqlite.execute(initModelsTable)
	
										
def initModelDB(modelName, columnNames , dbPath='~/.pycaskur/modeldb.db3')
	"""initialize a model table with filenames, this will be called when downloading a new model"""
	initModelTable = "CREATE TABLE %s(filename,%s)"""%','.join(columnNames)"


