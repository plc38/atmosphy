#todo: 
#	check if the BEGIN ITERATION statement is needed to write single files

import re
import pdb
import os
import sqlite3
from glob import glob
import numpy as np
import initialize
import urllib2

class casKurImportException(Exception):
	pass

def importModel(modelName, srcPath, dstPath = None, overwrite=False, verbose=False):
	if dstPath == None:
		dstPath = initialize.atmosStoragePath(modelName)

    # Check to see if the destination path exists
	if not os.path.exists(dstPath):
		os.makedirs(dstPath)
	modelData = splitModel(srcPath,dstPath)
	dbPath = initialize.atmosStoragePath('atmosphy.db3')
	conn = sqlite3.connect(dbPath)
	
	if len(conn.execute("	SELECT name FROM sqlite_master \
					WHERE type='table' AND \
					name='%s'"%modelName).fetchall()) == 1:
					
                        if overwrite:
                            # clear the table
                            raise Exception, 'test'

	initModelTable = """CREATE TABLE %s(filename STRING, 
    										teff DOUBLE,
    										logg DOUBLE,
    										feh DOUBLE,
    										alpha DOUBLE,
    										lh DOUBLE)"""%modelName
	conn.execute(initModelTable)

	for model in modelData:
		conn.execute('insert into %s values (?,?,?,?,?,?)'%modelName,tuple(model))

	conn.commit()
	conn.close()
	

def splitModel(srcPath, dstPath, overwrite=False, verbose=False):
	"""Imports the standard CasKur Modelgrid from srcPath and writes single files to dstPath"""
	srcPath = os.path.abspath(srcPath)
	dstPath = os.path.abspath(dstPath)
	modelData = []
	for fname in glob(os.path.join(srcPath,'*.dat')):
		modelSrc = file(fname).read()
		modelsRawData = re.split('B?EGIN\s+ITERATION\s+\d+\s+COMPLETED',modelSrc)

						 
		for model in modelsRawData:
			#problem with split
			if model == '\n': continue
			
			teffLoggMatch = re.search('T?EFF\s+(\d+\.\d*)\s+GRAVITY\s+(\d+\.\d*)',model)
			
			#searching for metallicity, alpha and microturbulence
			metalAlphaMatch = re.search('\[([+-]?\d+\.\d+)([ab]?)\]', model)
			microMatch = re.search('VTURB[ =]?(\d+\.\d+)',model)
			mixLengthMatch = re.search('ONVECTION (OFF|ON)\s+(\d+\.\d+)',model)
			
			#Checking the integrity of the model
			
			if teffLoggMatch == None:
				raise casKurImportException(
					"Current Model does not contain effective temperature:"
					"\n\n--------\n\n%s" % (model,))
			
			if metalAlphaMatch == None:
				raise casKurImportException(
					"Current Model does not contain metallicity information:"
					"\n\n--------\n\n%s" % (model,))

			if mixLengthMatch == None:
				raise casKurImportException(
					"Current Model does not contain mixing length information:"
					"\n\n--------\n\n%s" % (model,))

			
			#reading in the model parameters
			convertAlpha = {'':0.0, 'a':0.4, 'b':1.0}
			
			teff	= float(teffLoggMatch.groups()[0])
			logg 	= float(teffLoggMatch.groups()[1])
			feh		= float(metalAlphaMatch.groups()[0])
			alpha 	= convertAlpha[metalAlphaMatch.groups()[1]]
			mixing 	= float(mixLengthMatch.groups()[1])
			
			#writing to file
			newFName = "teff%.2f_logg%.3f_feh%.3f_alpha%.2f_lh%.2f.dat"%(teff, logg, feh, alpha, mixing)
			if verbose:
				print "Writing %s"%newFName
			newFPath = os.path.join(dstPath,newFName)
			file(os.path.join(dstPath,newFName),'w').write(model)
			modelData.append([os.path.join(dstPath,newFName),teff,logg,feh,alpha,mixing])
	return modelData
		
	
def getNextLine(dataIter):
	try:
		return dataIter.next().strip()
	except:
		raise casKurImportException('End of File before model end')

def readDeck(filePath):
	data = []
	rawIter = iter(file(filePath))
	deckStart = "READ DECK6"
	while True:
		line = getNextLine(rawIter)
		if line.startswith(deckStart): break # perhaps use regex so that it can pick up when the R is missing from READ DECK6? AC
		
	while True:
			line = getNextLine(rawIter)
			if line.startswith("PRADK"): # as above AC
#				self.pradk = float(line.split()[1])
				break
			data.append([float(item) for item in line.split()])
	return np.array(data)
	
class casKurModel(object):
	#Parsing a single caskur model and storing it in a datastructure
	@classmethod
	def fromFile(cls, fname):
		#reading in the raw string from a file with a single caskur Model
		fileData = file(fname).read()
		if len(re.split('BEGIN\s+ITERATION\s+\d+\s+COMPLETED',fileData))>2:
			raise casKurImportException("File contains multiple Models")

		return cls(fileData)
	
	def __init__(self,rawData):
		#modeldata
		data = []
		
		rawData = rawData.split("\r")
		rawIter = iter(rawData)
		#Looking for teff,logg, basically beginning of model
		while True:
			line = getNextLine(rawIter)
			tempLoggMatch = re.match("TEFF\s+(\d+\.\d*)\s+GRAVITY\s+(\d+\.\d*)\s+(\w+)\s*",line)
			if tempLoggMatch != None:
				self.teff = float(tempLoggMatch.groups()[0])
				self.logg = float(tempLoggMatch.groups()[1])
				self.modelType = tempLoggMatch.groups()[2]
				break
		#Looking for Deck
		deckStart = "READ DECK6" # match EAD DECK6?
		while True:
			line = getNextLine(rawIter)
			if line.startswith(deckStart): break
			
		while True:
			line = getNextLine(rawIter)
			if line.startswith("PRADK"): # match RADK?
				self.pradk = float(line.split()[1])
				break
			data.append([float(item) for item in line.split()])
		self.data = np.array(data)
		


  
  
def download(modelNames, overwrite=False, verbose=True, dbPath=initialize.atmosStoragePath('atmosphy.db3')):

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
    
    modelsPath = initialize.atmosStoragePath('models/')
    configFilename = initialize.atmosStoragePath('conf.d')
    
    parser = ConfigParser()
    if not os.path.exists(dbPath): raise ValueError, 'no database file found in %s' % dbPath
    if not os.path.exists(configFilename): raise ValueError, 'no configuration file found in %s' % configFilename
    
    parser.read(configFilename)
    
    # Get all the available model names from our configuration file
    availableModels = parser.options('models')
                  
    if (type(modelNames) == type(str())): modelNames = [modelNames]
    
    # Find all the models that match our wildmask given
    
    modelMatches = []
    for modelName in modelNames:
        modelMatches = modelMatches + fnmatch.filter(availableModels, modelName.lower())
    
    
    if (1 > len(modelMatches)): raise ValueError, 'no models found.'
    
    # Get the regular expression patterns for each model name
    
    modelStacks = {}
    
    for modelMatch in modelMatches:
        modelStacks[modelMatch] = parser.get('models', modelMatch).strip('"\'').split()

    
    # Get all the model files we need
    
    for modelName, modelFiles in modelStacks.iteritems():
    
        
        if verbose:
            print 'Entering %s' % modelName
        
        # Generate the models directory if it doesn't exist
        if not os.path.exists(modelsPath):
            if verbose:
                print 'Creating %s' % modelsPath
                
            os.makedirs(modelsPath)
        
        # Generate this specific model directory if it doesn't exist
        if not os.path.exists(os.path.join(modelsPath, modelName)):
            if verbose:
                print 'Creating %s' % modelsPath + modelName
            
            os.makedirs(os.path.join(modelsPath,modelName))

        
        for modelFile in modelFiles:
    
            # Check to see if this file already exists
            fullPath = os.path.join(modelsPath, modelName, modelFile.split('/')[-1])
            fileExists = os.path.exists(fullPath)
            
            if (overwrite and fileExists) or not fileExists:
                
                if verbose and not fileExists: print 'Writing %s from %s' % (fullPath, modelFile)
                if fileExists:
                    if verbose: print 'Over-writing %s with %s' % (fullPath, modelFile)
                    os.remove(fullPath)
                    
                stream = urllib2.urlopen(modelFile)
                data = stream.read()
                stream.close()
                

                
                newFile = open(fullPath, 'w')
                newFile.write(data)
                newFile.close()
		
        
        # Import the model into the database
        srcPath = os.path.join(modelsPath, modelName)
        dstPath = os.path.join(srcPath, 'split')
        
        importModel(modelName, srcPath, dstPath, overwrite=overwrite, verbose=verbose)

    
    

	