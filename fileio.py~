
import re
import pdb
import os
import sqlite3
from glob import glob
import numpy as np
import urllib2
import bz2
import cPickle as pickle
import hashlib


#import initialize
import modeldb
import logging, logging.config


# Establish logging parameters from ~/.atmosphy/logging.conf

#logging.config.fileConfig(atmosphyUserPath + '/logging.conf')


import fnmatch

class casKurImportException(Exception):
    pass


def md5_file(filename):
    import hashlib
    md5 = hashlib.md5()
    
    with open(filename,'rb') as f:
        for chunk in iter(lambda: f.read(128*md5.block_size), ''): 
             md5.update(chunk)
             
    return md5.hexdigest()


def importModel(modelName, modelID):
    
    "importing model into the database"
    
    
    atmosphy_path = os.path.expanduser('~/.atmosphy')
    
    conn = modeldb.getModelDBConn()
    deckShape = conn.execute('select ROWS, COLS from ATMOSPHY_CONF '
                             'where MODEL_NAME=?', (modelName,)).fetchone()
    for fname in glob(os.path.join(atmosphy_path, 'models', modelName, '*.dat')):
        modelSrc = file(fname).read()
        modelsRawData = re.split('B?EGIN\s+ITERATION\s+\d+\s+COMPLETED',modelSrc)
        
        for model in modelsRawData:
            #problem with split
            if model == '\n' or model == '': continue
            
            teffLoggMatch = re.search('T?EFF\s+(\d+\.\d*)\s+GRAVITY\s+(\d+\.\d*)',model)
            
            #searching for metallicity, alpha and microturbulence
            metalAlphaMatch = re.search('\[([\s+-]?\d+\.\d+)([aAbB]?)\]?', model)
            microMatch = re.search('VTURB[ =]?(\d+[\.\d+]?)',model)
            mixLengthMatch = re.search('ONVECTION (OFF|ON)\s+(\d+\.\d+)',model)
            pradkMatch = re.search('P?RADK (\d+\.\d+E[+-]?\d+)',model)
            
            #Checking the integrity of the model

            if teffLoggMatch == None:
                raise casKurImportException(
                    "Current Model does not contain effective temperature:"
                    "\n\n--------\n\n%s" % (model,))
    
                
                
            try:                    
                if metalAlphaMatch == None:
                    raise casKurImportException(
                        "Current Model does not contain metallicity information:"
                        "\n\n--------\n\n%s" % (model,))
            except casKurImportException:
                knownProblemFiles = ['ap00k2.dat','ap00k4.dat','asun.dat']
                if os.path.basename(fname) in knownProblemFiles:
                    continue
                else:
                    raise casKurImportException(
                        "Current Model does not contain metallicity information:"
                        "\n\n--------\n\n%s" % (model,))
                
            if mixLengthMatch == None:
                raise casKurImportException(
                    "Current Model does not contain mixing length information:"
                    "\n\n--------\n\n%s" % (model,))
    
            
            #reading in the model parameters
            convertAlpha = {'':0.0, 'a':0.4, 'b':1.0}
            
            teff    = float(teffLoggMatch.groups()[0])
            logg     = float(teffLoggMatch.groups()[1])
            feh        = float(metalAlphaMatch.groups()[0])
            alpha     = convertAlpha[metalAlphaMatch.groups()[1].lower()]
            micro    = float(microMatch.groups()[0])
            mixing     = float(mixLengthMatch.groups()[1])
            pradk    = float(pradkMatch.groups()[0])
            
            #reading model, pickling it and compressing it
            deck = readDeck(model)
            
            
            #fix for deck with only 71 points (there seems to be only one in ap05k2odfnew.dat)
            if modelName == 'castelli-kurucz' and deck.shape[0] == 71:
                continue
            if deck.shape != deckShape:
                raise ValueError('Deck shape missmatch: expected: %s got %s\n'
                                 'This should not happen please contact the developers of atmosphy' %
                                 (deckShape, deck.shape))
            
            
            #writing to db
            modeldb.insertModelData(conn, modelName, [modelID, teff, logg, feh, alpha, micro, mixing, deck])
    
    logging.info('Added all decks from model %s to db' % modelName)
    logging.info('Updating the atmosphy_conf table')
    conn.execute('update ATMOSPHY_CONF set rows=?,'
                 'cols=?, INSTALLED=? where ID=?',
                 (deck.shape[0], deck.shape[1], 1, modelID))
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
            
            if re.match("^P?RADK.*",line) != None:
                break

            data.append([float(item) for item in re.sub('\s+|(?<!E)[-|\s]', ' \g<0>', line).split()])

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
        


def installedModels():
    """
    
    Reads from the database and returns the models on disk
    
    """
    conn = modeldb.getModelDBConn()
    modelData = conn.execute("SELECT model_name FROM atmosphy_conf WHERE installed=1")
    modelNames = ([str(item[0]) for item in modelData])

    #modelNames.remove('models')
    
    return modelNames
    
def formatMOOG(Teff, logg, FeH, deck):

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
                    
        deck    :   array-type
                    The full deck values for the model atmosphere.
                         
                         
    Examples:
    =========
    
        MOOGformatting = formatMOOG(5000.0, 2.0, -3.0, [[3.02342, ... 5.23423], ..., [1.3423, ..., 8.233423]])
        
        myfile = open('modelatmosphere.mod', 'w')
        myfile.write(MOOGformatting)
        myfile.close()
        
        Here your modelatmosphere.mod file is ready to be interpreted by MOOG.
        
        
    """

    if type(deck) is type(None):
        raise ValueError('deck is missing')
        
    # Generate the output file name
    output = str(Teff).split('.')[0] + '_' + str(logg).replace('.', '')[0:2] + '_p' + str(FeH).replace('-', 'm')[0:2] + '.mod'
    output = output.replace('pm', 'm')
    

    content  = "KURUCZ\n"
    content += "          TEFF" + " " * (7 - len(str(Teff))) + "%6.0f.  GRAVITY %2.5f LTE\n" % (Teff, logg,)
    
    while True:
        if len(deck.shape) == 2:
            break
        elif len(deck.shape) > 2:
            deck = deck[0]
        elif len(deck.shape) < 2: raise ValueError
        
        
    content += "NTAU        %2.0f\n" % (len(deck),)
    
    for line in deck:
        
        # We need to account that the deck may contain a different number of columns on
        # different occasions
        
        # Since columns 1 and 2 have different formatting, then all the rest have the same
        # we will fill the rest
        tempLine = "% 2.8E% 9.1E" + (len(line) - 2) * "% 2.3E" + "\n"
        #tempLine = " %1.8E" +  " " * (9 - len(str(line[1]))) + "%5.1f" + " %1.3E" * (len(line) - 2) + "\n"
        content += tempLine % tuple(line,)
        
    content += "          2\n"
    content += "Natoms        0          %2.1f\n" % (FeH,)
    content += "NMOL          0\n"

    return content
    


      
def download(modelName, clobber=False, verbose=True, database='~/.atmosphy/atmosphy.db3'):

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

    
    atmosphy_path = os.path.expanduser('~/.atmosphy/')
    models_path = os.path.join(atmosphy_path, 'models')

    conn = modeldb.getModelDBConn()
    
    
    
    modelID = conn.execute('select ID from ATMOSPHY_CONF '
                           'where MODEL_NAME = ?',
                           (modelName,)).fetchall()
    
    
    #checking if this model does exist and is not installed
    if len(modelID) == 1:
        modelID = modelID[0][0]
        installed = conn.execute('select INSTALLED from ATMOSPHY_CONF '
                                 'where ID = ?', (modelID,)).fetchone()[0]
        if installed == 1:
            raise ValueError('Model %s is installed.' % modelName)
    elif len(modelID) == 0:
        availableModels = conn.execute('select MODEL_NAME from ATMOSPHY_CONF '
                                       'where INSTALLED = 0').fetchall()
        print "Available models:\n %s" % ','.join(availableModels)
        raise ValueError('Model %s does not exist' % modelName)
        
    
    
    
    # Generate the models directory if it doesn't exist
    if not os.path.exists(models_path):
        logging.info('Creating %s' % models_path)
        os.makedirs(models_path)
    
    # Generate this specific model directory if it doesn't exist
    modelDir = os.path.join(models_path, modelName)
    if not os.path.exists(os.path.join(models_path, modelName)):
        logging.info('Creating %s' % os.path.join(models_path, modelName))
        os.makedirs(os.path.join(models_path,modelName))
    
    
    #Getting models and checking MD5s
    
    curs = conn.cursor()
    
    
    
    for url, md5_hash in curs.execute('select URL, MD5_HASH from ATMOSPHY_URLS where MODEL_ID = ?', (modelID,)):
        filename = url.split('/')[-1]
        if os.path.exists(os.path.join(modelDir, filename)):
            print "Checking MD5 for %s" % os.path.join(modelDir, filename),
            curMD5 = md5_file(os.path.join(modelDir, filename))
            if md5_hash == curMD5:
                print "....Verified"
            else:
                print "....Failed. Redownloading."
                stream = urllib2.urlopen(url)
                data = stream.read()
                stream.close()
                
                newFile = open(os.path.join(modelDir, filename), 'w')
                newFile.write(data)
                newFile.close()
                
        else:
            print "Downloading from %s" % url
            stream = urllib2.urlopen(url)
            data = stream.read()
            stream.close()
            
            newFile = open(os.path.join(modelDir, filename), 'w')
            newFile.write(data)
            newFile.close()

    
    logging.info('Importing models ...')
    importModel(modelName, modelID)
    logging.info('Successfully imported %s model' % (modelName,))
    logging.info('Done!.')
    

    
