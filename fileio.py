#todo: 
#	check if the BEGIN ITERATION statement is needed to write single files

import re
import pdb
import os
import sqlite3
from glob import glob
import numpy as np
import initialize

class casKurImportException(Exception):
	pass

def casKurImportModel(modelName, srcPath, dstPath = None):
	if dstPath == None:
		dstPath = os.path.join(os.path.expanduser('~/.pycaskur/'),modelName)
		if not os.path.exists(dstPath):
			os.makedirs(dstPath)
	modelData = casKurSplitModel(srcPath,dstPath)
	dbPath = initialize.getDBPath()
	conn = sqlite3.connect(dbPath)
	
	if len(conn.execute("	SELECT name FROM sqlite_master \
					WHERE type='table' AND \
					name='%s'"%modelName).fetchall()) == 1:
					raise Exception('test')
	initModelTable = """CREATE TABLE %s(filename STRING, 
    										teff DOUBLE,
    										logg DOUBLE,
    										feh DOUBLE)"""%modelName
	conn.execute(initModelTable)

	for model in modelData:
		conn.execute('insert into %s values (?,?,?,?)'%modelName,tuple(model))

	conn.commit()
	conn.close()

def casKurSplitModel(srcPath,dstPath):
	"""Imports the standard CasKur Modelgrid from srcPath and writes single files to dstPath"""
	srcPath = os.path.abspath(srcPath)
	dstPath = os.path.abspath(dstPath)
	modelData = []
	for fname in glob(os.path.join(srcPath,'*.dat')):
		modelSrc = file(fname).read()
		modelsRawData = re.split('BEGIN\s+ITERATION\s+\d+\s+COMPLETED',modelSrc)
		metalMatch = re.search('a([mp]?\d+)',fname)
		if metalMatch == None: raise casKurImportException("Can't determine metallicity from filename, searching for a([mp]?\d+)")

		metallicity = -.1*float(metalMatch.groups()[0][1:])\
						 if metalMatch.groups()[0][0]=='m'\
						 else .1*float(metalMatch.groups()[0][1:]) 
						 
		for model in modelsRawData:
			#problem with split
			if model == '\n': continue
			
			teffLoggMatch = re.search('TEFF\s+(\d+\.\d*)\s+GRAVITY\s+(\d+\.\d*)\s+(\w+)\s*',model)
			if teffLoggMatch == None:
				raise casKurImportException("Current Model does not contain effective\
				 temperature:\n\n--------\n\n%s"%model)
				 
			teff = float(teffLoggMatch.groups()[0])
			logg = float(teffLoggMatch.groups()[1])
			
			newFName = "teff%.2f_logg%.3f_feh%.3f.dat"%(teff,logg,metallicity)
			print "Writing %s"%newFName
			newFPath = os.path.join(dstPath,newFName)
			file(os.path.join(dstPath,newFName),'w').write(model)
			modelData.append([os.path.join(dstPath,newFName),teff,logg,metallicity])
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
		if line.startswith(deckStart): break
		
	while True:
			line = getNextLine(rawIter)
			if line.startswith("PRADK"):
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
		deckStart = "READ DECK6"
		while True:
			line = getNextLine(rawIter)
			if line.startswith(deckStart): break
			
		while True:
			line = getNextLine(rawIter)
			if line.startswith("PRADK"):
				self.pradk = float(line.split()[1])
				break
			data.append([float(item) for item in line.split()])
		self.data = np.array(data)
		

			
		

				
	