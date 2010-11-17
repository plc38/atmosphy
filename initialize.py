import sqlite3
import os

def getDBPath():
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf.d','pycaskur.db3')

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
    	
    	

  
  
    def download(self, modelNames, overwrite=False, verbose=True):
    
        """
        Download the given model(s) from the Kurucz website and load them into your database.
        
        Parameters:
        ===========
        
        modelNames  :   string or list
                        Downloads all of the model names suppled, or any that match the wildmask supplied.
        
                        
        Available models:
        =================
        
            Kurucz          :   Kuruczs grids of model atmospheres, as described in X
            
            Kurucz-NOVER    :   Kurucz models with no convective overshooting computed by Fiorella Castelli
                                [castelli@ts.astro.it] in Trieste. The convective treatment is described in
                                Castelli, Gratton, and Kuruczs 1997, A&A 328, 841.
                                
            Kurucz-ODFNEW   :   Kurucz models as NOVER but with newly computed ODFs with better opacities
                                and better abundances.
                                
            Kurucz-AODFNEW  :   Kurucz models as per ODFNEW but with Alpha enhancement. The alpha-process
                                elements (O, Ne, Mg, Si, S, Ar, Ca, and Ti) enhanced by +0.4 in the log and
                                Fe -4.53

        
        
        Examples:
        =========
        
            download('Kurucz')          :   Download the standard Kurucz grid models.
            
            download('Kurucz-*ODFNEW')  :   This will download both the Kurucz-AODFNEW and the Kurucs-ODFNEW
                                            model as they both match the wildmask given.
    
        """
        
        import fnmatch
        from ConfigParser import ConfigParser
        
        parser = ConfigParser()
        if not os.path.exists(os.path.dirname(getDBPath()) + '/conf.d'): raise ValueError, 'no configuration file found in %s' % os.path.dirname(getDBPath()) + '/conf.d'
        
        parser.read(os.path.dirname(getDBPath()) + '/conf.d')
        
        # Get all the available model names from our configuration file
        availableModels = config.options('models')
                      
        if (type(modelNames) == type(str())): modelNames = [modelNames]
        
        # Find all the models that match our wildmask given
        
        modelMatches = []
        for modelName in modelNames:
            modelMatches = modelMatches + fnmatch.filter(availableModels, modelName.lower())
        
        
        if (1 > len(modelMatches)): raise ValueError, 'no models found'
        
        # Get the regular expression patterns for each model name
        
        modelStacks = {}
        
        for modelMatch in modelMatches:
            modelStacks[modelMatch] = parser.get('models', modelMatch).strip('"\'').split()

        
        # Get all the model files we need
        
        for modelName, modelFiles in modelStacks.iteritems():
        
            
            if verbose:
                print 'Entering %s' % modelName
            
            # Generate the models directory if it doesn't exist
            if not os.path.exists(os.path.dirname(getDBPath()) + 'models/'):
                if verbose:
                    print 'Creating %s' % os.path.dirname(getDBPath()) + '/models/'
                    
                os.system('mkdir %s' % os.path.dirname(getDBPath()) + '/models/')
            
            # Generate this specific model directory if it doesn't exist
            if not os.path.exists(os.path.dirname(getDBPath()) + 'models/' + modelName + '/'):
                if verbose:
                    print 'Creating %s' % os.path.dirname(getDBPath()) + '/models/' + modelName
                
                os.system('mkdir %s' % os.path.dirname(getDBPath()) + '/models/' + modelName)
    
            
            for modelFile in modelFiles:
        
                # Check to see if this file already exists
                fullPath = os.path.dirname(getDBPath()) + '/models/' + modelName + '/' + modelFile.split('/')[-1]
                fileExists = os.path.exists(fullPath)
                
                if (overwrite and fileExists) or not fileExists:
                    
                    if verbose and not fileExists: print 'Writing %s from %s' % (fullPath, modelFile)
                    if fileExists:
                        if verbose: print 'Over-writing %s with %s' % (fullPath, modelFile)
                        os.system('rm -f %s' % fullPath)
                        
                    stream = urllib2.urlopen(modelFile)
                    data = stream.read()
                    stream.close()
                    

                    
                    newFile = open(fullPath, 'w')
                    newFile.write(data)
                    newFile.close()
                    
                    
        
        # todo - import into database
                
                
    
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





