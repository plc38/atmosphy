import sqlite3
import os



class modelDB():

    def __init__(self, dbPath='~/.pycaskur/modeldb.db3'):
    
    	"""Initialize the database with a model at the dbPath location"""
    	
    	self.dbPath = dbPath
    	dbPath = os.path.abspath(dbPath)
    	
    	initModelsTable = """CREATE TABLE models(model_name STRING, 
    										model_description STRING,
    										model_url STRING,
    										model_ondisk BOOL DEFAULT 0)"""
    	
    	if os.path.exists(dbPath): print "Warning: Overwriting database"
    	
    	#sqlite3.connect(os.path.abspath(dbPath))
    	#sqlite3.execute(initModelsTable)
    	
    	return None
    	
    	

  
  
    def getModels(self, modelNames):
    
        """
        Download the given model(s) from the Kurucz website and load them into your database.
        
        Parameters:
        ===========
        
        modelNames  :   string or list
                        Downloads all of the model names suppled, or any that match the wildmask supplied.
        
                        
        Available models:
        =================
        
        
        GRIDM01             :   
        GRIDM02             :   
        GRIDM03             :   
        GRIDM05             :   
        GRIDM05ODFNEW       :
        GRIDM05AODFNEW      :
        GRIDM05NOVER        :
        GRIDM10             :
        GRIDM10ANOVER       :
        GRIDM10AODFNEW      :
        GRIDM10HE50         :
        GRIDM10NOVER        :
        GRIDM10ODFNEW       :
        GRIDM15             :
        GRIDM15NOVER        :
        GRIDM15ODFNEW       :
        GRIDM15ANOVER       :
        GRIDM15AODFNEW      :
        GRIDM20             :
        GRIDM20NOVER        :
        GRIDM20ODFNEW       :
        GRIDM20ANOVER       :
        GRIDM20AODFNEW      :
        GRIDM25             :
        GRIDM25NOVER        :
        GRIDM25ODFNEW       :
        GRIDM25ANOVER       :  
        GRIDM25AODFNEW      :   
        GRIDM30             :
        GRIDM35             :
        GRIDM40             :
        GRIDM40AODFNEW      :
        GRIDM45             :
        GRIDM50             :
        GRIDP00             :
        GRIDP00AODFNEW      :
        GRIDP00NOVER        :
        GRIDP00ODFNEW       :
        GRIDP01             :
        GRIDP02             :
        GRIDP02ODFNEW       :
        GRIDP03             :
        GRIDP04             :
        GRIDP05             :
        GRIDP05NOVER        :
        GRIDP05ODFNEW       :
        GRIDP05AODFNEW      :
        GRIDP10             :
        GRIDHBETA           :
        GRIDHBETACASTELLI   :

        
        
        Examples:
        =========
        
        getModels('GRIDM*')  - This will download all models matching the name 'GRIDM*'
        
        getModels(['GRIDM02', 'GRIDH*']) - This will download the GRIDM02 model and all the models matching
                                            the wildmask 'GRIDH*'        
        
        
        """
        
        import fnmatch

        availableModels = [
                             'GRIDM01',
                             'GRIDM02',
                             'GRIDM03',
                             'GRIDM05',
                             'GRIDM05ODFNEW',
                             'GRIDM05AODFNEW',
                             'GRIDM05NOVER',
                             'GRIDM10',
                             'GRIDM10ANOVER',
                             'GRIDM10AODFNEW',
                             'GRIDM10HE50',
                             'GRIDM10NOVER',
                             'GRIDM10ODFNEW',
                             'GRIDM15',
                             'GRIDM15NOVER',
                             'GRIDM15ODFNEW',
                             'GRIDM15ANOVER',
                             'GRIDM15AODFNEW',
                             'GRIDM20',
                             'GRIDM20NOVER',
                             'GRIDM20ODFNEW',
                             'GRIDM20ANOVER',
                             'GRIDM20AODFNEW',
                             'GRIDM25',
                             'GRIDM25NOVER',
                             'GRIDM25ODFNEW',
                             'GRIDM25ANOVER',
                             'GRIDM25AODFNEW',
                             'GRIDM30',
                             'GRIDM35',
                             'GRIDM40',
                             'GRIDM40AODFNEW',
                             'GRIDM45',
                             'GRIDM50',
                             'GRIDP00',
                             'GRIDP00AODFNEW',
                             'GRIDP00NOVER',
                             'GRIDP00ODFNEW',
                             'GRIDP01',
                             'GRIDP02',
                             'GRIDP02ODFNEW',
                             'GRIDP03',
                             'GRIDP04',
                             'GRIDP05',
                             'GRIDP05NOVER',
                             'GRIDP05ODFNEW',
                             'GRIDP05AODFNEW',
                             'GRIDP10',
                             'GRIDHBETA',
                             'GRIDHBETACASTELLI'
                         ]
                      
        if (type(modelNames) == type(str())): modelNames = [modelNames]
        
        modelStack = []
        for modelName in modelNames:
            modelStack = modelStack + fnmatch.filter(availableModels, modelName.upper())
            
        # Download all the model name files and for each one, create the directory in the .pycaskur database

    
    def populate(self, modelName, dbPath=None, directory=os.getcwd() + '/', wildmask='*.dat', verbose=False):
        """
        
        Populates a database with the attributes of the models available.
        These files are assumed to be in the #todo CasKur file format, i.e.
        
        fehp342_teff4500_logg32.dat
        
        
        Parameters:
        ===========
        
        modelName   : string
                    The name of the model.
                    
        dbPath      : string, optional
                    The database filename path. If unspecified it defaults to your standard pycaskur database path.
        
        directory   : string, optional
                    The directory folder where your model files are stored.
                    
        wildmask    : string, optional
                    A wildmask string that matches your model files.
                    
        """
    
        import glob
        if (dbPath == None): dbPath = self.dbPath
        
        models = []
        modelFilenames = glob.glob(directory + wildmask)
        
        
        
        for modelFilename in modelFilenames:
            
            try:
                feh, teff, logg = modelFilename.split('_')
                
            except ValueError:
                if verbose:
                    raise Warning, "ignoring invalid model file format '%s'" % modelFilename
                    
            else:
                # Add this to our list of models
                
                models.append([modelFilename, feh, teff, logg])
                
        # todo - rewrite to make the data sql-safe?
        query = "INSERT INTO TABLE ? (filename, feh, teff, logg) VALUES ('" + "'), ('".join(["','".join(model) for model in models]) + "');"
        
        return sql.execute(query, modelName)
    
    
    
    
    
										
#def initModelDB(modelName, columnNames , dbPath='~/.pycaskur/modeldb.db3'):
#	"""initialize a model table with filenames, this will be called when downloading a new model"""
#	initModelTable = "CREATE TABLE %s(filename,%s)"""%','.join(columnNames)"





