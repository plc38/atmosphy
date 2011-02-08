import numpy as np
from scipy import interpolate
import glob
import os
import sqlite3
import cPickle as pickle
import zlib

import fileio
import initialize
import modeldb

def getInterpModels(interpolatedDimensions, SQL, boundaryValues):

    conn = modeldb.getModelDBConnection()
    
    dimensions = ', '.join(interpolatedDimensions)
    
    if len(dimensions) > 0:
        positions = conn.execute('select %s %s' % (dimensions, SQL,),
                                    boundaryValues).fetchall()
        # There is a bug that if the length of each position is one, then instead
        # of returning a tuple it should return a float
        
        for i, position in enumerate(positions):
            if len(position) == 1:
                positions[i] = position[0]
    
    else: positions = []    
     
                                    
    modelGrid = conn.execute('select deck %s' % (SQL,),
                                boundaryValues).fetchall()
    conn.close()
    
    return positions, np.array(zip(*modelGrid)[0])


def interpModelGrid(modelName, Teff, logg, FeH, k=2.0, alpha=0.0, level=1, method='linear'):

    """
    
    Interpolates in N-dimensional space to find the given point
    (Teff, logg, FeH, k, alpha) given the model name.
    
    Parameters:
    ===========
    
    modelName   : string
                  The name of the model to lookup in your local SQL database.

    Teff        : float
                  The effective temperature (Teff in Kelvin) of the star you plan to interpolate for.
              
    FeH         : float
                  The metallicity ([Fe/H]) of the star you plan to interpolate for.
                
    logg        : float
                  The surface gravity (log g) of the star you plan to interpolate for.
            
    k           : float, optional (default = 2.0)
                  The turbulence in the atmosphere of the star (km/s).
                  
    alpha       : float, optional (default = 0.0)
                  The level of alpha enhancement of the star ([alpha/Fe] in dex).
            
    level       : integer, optional (default = 1)
                  The maximum number of levels on either side of the point you wish to return in each
                  dimension.
                  
    method      : string, optional (default = 'linear')
                  The interpolation method which is passed to scipy.interpolate.griddata.
                  
                  Options are 'linear', 'nearest', or 'cubic'. 
    
    """

    # Our grid point in N dimensionsal space
    gridSpace = {
                    'teff' : Teff,
                    'logg' : logg,
                    'feh'  : FeH,
                    'k'    : k,
                    'alpha': alpha
                 }
                
    
    # Find the nearest neighbours in N dimensions, and get the SQL
    interpolatedDimensions, SQL, boundaryValues = getNearestNeighbours(modelName, Teff, logg, FeH, k, alpha, level=level)

    # Populate the model grid
    modelGridCoord, modelGrid = getInterpModels(interpolatedDimensions, SQL, boundaryValues)
    
    # If there are no grid points to interpolate between then no interpolation is necessary
    if len(modelGridCoord) == 0: return modelGrid[0]

    # Update our grid point based on interpolatedDimensions
    gridPoint = []
    for interpolatedDimension in interpolatedDimensions:
        gridPoint.append(gridSpace[interpolatedDimension])
        
    print np.array(modelGridCoord).shape, np.array(modelGrid).shape, np.array(gridPoint).shape
    # Return the interpolated grid deck
    return interpolate.griddata(modelGridCoord, modelGrid, gridPoint, method=method)
    
    
    
    
    
def getNearestNeighbours(model, Teff, logg, FeH, k=2.0, alpha=0.0, level=1):

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

    

    connection = modeldb.getModelDBConnection()

    result = connection.execute('select Teff, logg, FeH, k, alpha from `%s`' % model)
    
    # todo - consider rewriting following section into a loop?
    Teff_grid, logg_grid, FeH_grid, k_grid, alpha_grid = zip(*result.fetchall())
    connection.close()
    
    grid = zip(Teff_grid, logg_grid, FeH_grid, k_grid, alpha_grid)
    
    
    # Find the nearest N levels of indexedFeHs
    FeH_neighbours  = get1Dneighbours(FeH_grid, FeH, level=level)

    # Find the Teff available for our FeH possibilites
    Teff_available = [point[0] for point in grid if point[2] in FeH_neighbours]
    Teff_neighbours = get1Dneighbours(Teff_available, Teff, level=level)
    
    # Find the logg available for our FeH and Teff possibilities
    logg_available = [point[1] for point in grid if point[2] in FeH_neighbours and point[0] in Teff_neighbours]
    logg_neighbours = get1Dneighbours(logg_available, logg, level=level)
    
    # Find the k available for our FeH, Teff, and logg restricted 
    k_available = [point[3] for point in grid if point[2] in FeH_neighbours and point[0] in Teff_neighbours and point[1] in logg_neighbours]
    k_neighbours = get1Dneighbours(k_available, k, level=level)
    
    # Find the alpha available for our FeH, Teff, logg, and k restricted
    alpha_available = [point[4] for point in grid if point[2] in FeH_neighbours and point[0] in Teff_neighbours and point[1] in logg_neighbours and point[3] in k_neighbours]
    alpha_neighbours = get1Dneighbours(alpha_available, alpha, level=level)
    
    
    # Build the dimensions we want back from the SQL table
    
    SQL = 'from `%s` where' % model
    
    boundaryValues = []
    interpolatedDimensions = []
    
    availableDimensions = {    
                            'feh'   : FeH_neighbours,
                            'teff'  : Teff_neighbours,
                            'logg'  : logg_neighbours,
                            'k'     : k_neighbours,
                            'alpha' : alpha_neighbours,
                            }
                            
    for dimension, value in zip(['teff', 'logg', 'feh', 'k', 'alpha'], [Teff, logg, FeH, k, alpha]):
        neighbours = availableDimensions[dimension]
            
        # If only one 'neighbour' is present, then this dimension does not need to be interpolated upon
        if (len(neighbours) > 1):
            interpolatedDimensions.append(dimension)
        
            # Add these limits for the sql query
            boundaryValues.append(min(neighbours))
            boundaryValues.append(max(neighbours))
            
            SQL += ' %s between ? and ? and' % dimension 
        
        else:
        
            boundaryValues.append(value)
            
            SQL += ' %s = ? and' % dimension
    
    if SQL[-3:] == 'and': SQL = SQL[:-3]
    
    # Return the SQL
    return (interpolatedDimensions, SQL, tuple(boundaryValues))
       
    
                                   
        
        
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
    
    if (1 > len(data)): return data
    
    offset = np.array(data) - point
    
    # If there is an exact point that we want, then we don't want to interpolate at all        
    if 0.0 in offset: return [point]
    
    # we want level points on either side
    
    # split into positive and negative first
    
    pos = filter(lambda x: x > 0, offset)
    neg = filter(lambda x: x < 0, offset)
    
    # If there are none positive, or none negative then this point is outside the bounds of the grid
    if (1 > len(pos)) or (1 > len(neg)):
        raise OutOfBoundsError('the given data point (%2.4f) is outside the bounds of the grid (%2.4f, %2.4f)' % (point, min(data), max(data),))

    # We may have duplicates of the same value, which is screwy with levels

    posUnique = np.unique(pos)
    negUnique = np.unique(neg)

    neighbours = np.array(list(posUnique)[0:level] + list(negUnique)[-level:])
    neighbours += point
    
    # May not be necessary
    neighbours.sort()
    
    return neighbours


class OutOfBoundsError(Exception):
    pass