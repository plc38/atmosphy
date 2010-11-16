import fileio
import numpy as np
from scipy import interpolate
def getInterpModels(fileNames):
	modelGrid = []
	for fname in fileNames:
		modelGrid.append(fileio.readDeck(fname))
	return np.array(modelGrid)
#rewrite with **kwargs
def interpModelGrid(teff, logg, feh, modelName):
	positions, fileNames = lkdfjgldfkjgldfkgjdflgj
	modelGrid = getInterpModels(fileNames)
	return interpolate.griddata(positions, modelGrid, (teff, logg, feh),method='linear')