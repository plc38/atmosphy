import numpy as np
from scipy import interpolate
import glob
import os
import sqlite3
import pdb
import fileio
import initialize


def getInterpModels(fileNames):
	modelGrid = []
	for fname in fileNames:
		modelGrid.append(fileio.readDeck(fname))
	return np.array(modelGrid)
#rewrite with **kwargs
def interpModelGrid(Teff, logg, FeH, modelName):

	modelData = getNearestNeighbours(modelName, Teff, logg, FeH)
	fileNames = zip(*modelData)[0]
	modelGridCoord = np.array(zip(*modelData)[1:]).transpose()
	modelGrid = getInterpModels(fileNames)

	return interpolate.griddata(modelGridCoord, modelGrid, (Teff, logg, FeH),method='linear')
	
	
def getNearestNeighbours(model='caskur', Teff=None, logg=None, FeH=None, k=2.0, level=1):

    """
    
    Finds the nearest neighbours to a point in a multi-dimensional grid.
    
    
    Parameters:
    ===========
    
    FeH     : float
              The metallicity ([Fe/H]) of the star you plan to interpolate for.
            
    Teff    : float
              The effective temperature (Teff in Kelvin) of the star you plan to interpolate for.
    
    logg    : float
              The surface gravity (log g) of the star you plan to interpolate for.
            
    k       : float, optional
              The turbulence in the atmosphere of the star (km/s).
            
    level   : integer, optional
              The maximum number of levels on either side of the point you wish to return in each
              dimension.
    """
    

    if (1 > level): raise ValueError, 'level must be a positive integer'
    if (Teff < 0): raise ValueError, 'Teff must be a positive float'
    if (logg < 0): raise ValueError, 'logg must be a positive float'
    if (k < 0): raise ValueError, 'k must be a positive float'

    

    connection = sqlite3.connect(initialize.getDBPath())

    result = connection.execute('select feh, teff, logg from %s' % model)
    FeH_grid, Teff_grid, logg_grid = zip(*result.fetchall())
    
    grid = zip(Teff_grid, logg_grid, FeH_grid)
    
    
    # Find the nearest N levels of indexedFeHs
    FeH_nearest  = get1Dneighbours(FeH_grid, FeH, level=level)

    # Find the Teff available for our FeH possibilites
    Teff_available = [point[0] for point in grid if point[2] in FeH_nearest]

    # Find the nearest N levels of Teff_available to Teff
    Teff_nearest = get1Dneighbours(Teff_available, Teff, level=level)
    
    # Find the logg available for our FeH and Teff possibilities
    logg_available = [point[1] for point in grid if point[2] in FeH_nearest and point[0] in Teff_nearest]
    
    # Find the nearest N levels of logg_available to logg
    logg_nearest = get1Dneighbours(logg_available, logg, level=level)

    # Grab back the filenames of these grid points
    
    gridLimits = tuple([min(FeH_nearest), max(FeH_nearest), min(Teff_nearest), max(Teff_nearest), min(logg_nearest), max(logg_nearest)])
    result = connection.execute('select filename, teff, logg, feh from %s where feh between ? and ? and teff between ? and ? and logg between ? and ?' % model, gridLimits)
   
   
    
    return result.fetchall()
   
    
    
                                    
        
        
def get1Dneighbours(data, point, level=1):
    """
    
    Returns closest neighbours on either side of the point provided.

    Parameters:
    ===========
    
    data    : array
            The data points used to find neighbours from.
            
    point   : float
            The point used to look for neighbours.
            
    level   : integer, optional
            The number of neighbours to find on either side of the point.
    """
    
    offset = np.array(data) - point
    
    # If there is an exact point that we want, then we don't want to interpolate at all        
    if 0.0 in offset: return [point]
    
    # we want level points on either side
    
    # split into positive and negative first
    
    pos = filter(lambda x: x > 0, offset)
    neg = filter(lambda x: x < 0, offset)

    # We may have duplicates of the same value, which is screwy with levels

    posUnique = np.unique(pos)
    negUnique = np.unique(neg)

    neighbours = np.array(list(posUnique)[0:level] + list(negUnique)[-level:])
    neighbours += point
    
    # May not be necessary
    neighbours.sort()
    
    return neighbours
