
import re
import pdb
import os
import sqlite3
from glob import glob
import numpy as np
import urllib2
import zlib
import cPickle as pickle


import initialize
import modeldb

import fnmatch
from ConfigParser import ConfigParser

class casKurImportException(Exception):
	pass

def importModel(modelName, srcPath, dstPath = None, clobber=False):
	
	"importing model into the database"
	
	if dstPath == None:
		dstPath = initialize.atmosStoragePath(modelName)

	modelSrc = ""
	for fname in glob(os.path.join(srcPath,'*.dat')):
		modelSrc += file(fname).read()

	modelsRawData = re.split('B?EGIN\s+ITERATION\s+\d+\s+COMPLETED',modelSrc)

    # Check to see if the destination path exists
	if not os.path.exists(dstPath):
		os.makedirs(dstPath)
		

	modeldb.initModelTable(modelName)
	
	conn = modeldb.getModelDBConnection()
	
	
	for model in modelsRawData:
		#problem with split
		if model == '\n': continue
		
		teffLoggMatch = re.search('T?EFF\s+(\d+\.\d*)\s+GRAVITY\s+(\d+\.\d*)',model)
		
		#searching for metallicity, alpha and microturbulence
		metalAlphaMatch = re.search('\[([+-]?\d+\.\d+)([ab]?)\]', model)
		microMatch = re.search('VTURB[ =]?(\d+\.\d+)',model)
		mixLengthMatch = re.search('ONVECTION (OFF|ON)\s+(\d+\.\d+)',model)
		pradkMatch = re.search('P?RADK (\d+\.\d+E[+-]?\d+)',model)
		
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
		pradk	= float(pradkMatch.groups()[0])
		
		#reading model, pickling it and compressing it
		deck = readDeck(model)
		zipdDeck = zlib.compress(pickle.dumps(deck))
		
		#writing to db
		modeldb.insertModelData(conn, modelName, [teff, logg, feh, alpha, mixing, pradk, zipdDeck])
		
	conn.commit()
	conn.close()
	

			 

		
	
def getNextLine(dataIter):
	try:
		return dataIter.next().strip()
	except:
		raise casKurImportException('End of File before model end')

def readDeck(modelString):
	data = []
	rawIter = iter(re.split('\r|\n',modelString))
	deckStart = "READ DECK6"
	while True:
		line = getNextLine(rawIter)
		if re.match("^R?EAD DECK.*",line) !=None: 
			break
		
	while True:
			line = getNextLine(rawIter)
			
			if re.match("^PRADK.*",line) != None:
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
		


  
  
def availableModels():
    
    """
    
    Reads from the astrophy config file and returns a dictionary of available model names
    and their relevant descriptions.
    
    """
    
    configFilename = initialize.atmosStoragePath('models.d')
    
    parser = ConfigParser()
    parser.read(configFilename)
    
    modelNames = parser.sections() #here
    
    availableModels = {}
    
    for modelName in modelNames:
        availableModels[modelName] = parser.get(modelName, 'description')
        
    return availableModels
    
    
def generateMOOG(Teff, logg, FeH, nTau, deck):

    """
    
    Generates a MOOG-compatible string containing the given stellar parameters (Teff, logg, FeH, nTau)
    and a given stellar atmosphere deck.
    
    Parameters:
    ===========
    
        Teff    :   float
                    The effective temperature of the model star (Kelvin).
                    
        logg    :   float
                    The surface gravity of the model star.
        
        FeH     :   float
                    The metallicity ([Fe/H]) of the model star.
                
        nTau    :   float
                    The nTau value of the model atmosphere.
                    
        deck    :   array-type
                    The full (floating point) deck values for the model atmosphere.
                         
                         
    Examples:
    =========
    
        MOOGformatting = generateMOOG(5000.0, 2.0, -3.0, 1.672, [[3.02342, ... 5.23423], ..., [1.3423, ..., 8.233423]])
        
        myfile = open('modelatmosphere.mod', 'w')
        myfile.write(MOOGformatting)
        myfile.close()
        
        Here your modelatmosphere.mod file is ready to be interpreted by MOOG.
        
        
    """
    # todo - does nTau value need to be interpolated between like the deck?

    if (type(deck) == type(None)):
        raise ValueError('deck is missing')
        
    # Generate the output file name
    output = str(Teff).split('.')[0] + '_' + str(logg).replace('.', '')[0:2] + '_p' + str(FeH).replace('-', 'm')[0:2] + '.mod'
    output = output.replace('pm', 'm')
    

    content  = "KURUCZ\n"
    content += "          TEFF   %6.0f.  GRAVITY %2.5f LTE\n" % (Teff, logg,)
    # todo - do we need to specify anything else here?
    
    content += "NTAU        %2.0f\n" % (nTau,)
    
    for line in deck:
        
        # We need to account that the deck may contain a different number of columns on
        # different occasions
        
        # Since columns 1 and 2 have different formatting, then all the rest have the same
        # we will fill the rest
        tempLine = " %1.8E" +  " " * (7 - len(round(Teff))) + "%5.1f" + " %1.3E" * (len(line) - 2) + "\n"
        content += tempLine % line
        
    content += "          2\n"
    content += "Natoms        0          %2.1f\n" % (FeH,)
    content += "NMOL          0\n"

    #moog = open(output, 'w')
    #moog.write(content)
    #moog.close()
    
    return content
    


      
def download(modelNames, overwrite=False, verbose=True, dbPath=initialize.atmosStoragePath('atmosphy.db3')):

    """
    
    Download the given model(s) from the Kurucz awebsite and load them into your database.
    
    
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

    
    modelsPath = initialize.atmosStoragePath('models/')
    configFilename = initialize.atmosStoragePath('conf.d')
    
    parser = ConfigParser()
    if not os.path.exists(dbPath): raise ValueError, 'no database file found in %s' % dbPath
    if not os.path.exists(configFilename): raise ValueError, 'no configuration file found in %s' % configFilename
    
    parser.read(configFilename)
    
    # Get all the available model names from our configuration file
    availableModels = parser.sections() #here
                  
    if (type(modelNames) == type(str())): modelNames = [modelNames]
    
    # Find all the models that match our wildmask given
    
    modelMatches = []
    for modelName in modelNames:
        modelMatches = modelMatches + fnmatch.filter(availableModels, modelName.lower())
    
    
    if (1 > len(modelMatches)): raise ValueError, 'no models found.'
    
    # Get the regular expression patterns for each model name
    
    modelStacks = {}
    
    for modelMatch in modelMatches:
        modelStacks[modelMatch] = parser.get(modelMatch, 'files').strip('"\'').split()

    
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
        
        if verbose:
            print 'Importing model...'
        importModel(modelName, srcPath, dstPath, overwrite=overwrite, verbose=verbose)

    
    

	