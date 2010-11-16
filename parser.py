
import glob
import os
import scipy
import sqlite3

def getDBPath():
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf.d','pycaskur.db3')


class pyCasKur():


    def __init__(self, folder=os.getcwd() + '/'):
    
        self.folder = folder
        
        
        return None
        
        
    
    def getNearestNeighbours(self, model='caskur', FeH=None, Teff=None, logg=None, k=2.0, level=1):
    
        """
        
        Finds the nearest neighbours from a directory of Kurucz model files.
        
        Parameters:
        ===========
        
        FeH     : float
                The metallicity ([Fe/H]) of the star you plan to interpolate for.
                
        Teff    : float
                The effective temperature (Teff in Kelvin) of the star you plan to interpolate for.
        
        logg    : float
                The surface gravity (log g) of the star you plan to interpolate for.
                
        k       : float
                The turbulence in the atmosphere of the star (km/s).
        """
        

        if (1 > level):
            raise ValueError, 'level must be a positive integer'

        

        connection = sqlite3.connect(getDBPath())
    
        result = connection.execute('select feh, teff, logg from %s' % modelName)
        FeH_grid, Teff_grid, logg_grid = zip(*result.fetchall())
        
        grid = zip(FeH_grid, Teff_grid, logg_grid)
        
        
        # Find the nearest N levels of indexedFeHs
        FeH_nearest  = self.__getLevels(FeH_grid, FeH, level=level)

        # Find the Teff available for our FeH possibilites
        Teff_available = [point[1] for point in grid if point[0] in FeH_nearest]

        # Find the nearest N levels of Teff_available to Teff
        Teff_nearest = self.__getLevels(Teff_available, Teff, level=level)
        
        # Find the logg available for our FeH and Teff possibilities
        logg_available = [point[2] for point in grid if point[0] in FeH_nearest and point[1] in Teff_nearest]
        
        # Find the nearest N levels of logg_available to logg
        logg_nearest = self.__getLevels(logg_available, logg, level=level)

        # Grab back the filenames of these grid points
        
        gridLimits = tuple([min(FeH_nearest), max(FeH_nearest), min(Teff_nearest), max(Teff_nearest), min(logg_nearest), max(logg_nearest)])
        result = connection.execute('select filename, feh, teff, logg from %s where feh between ? and ? and teff between ? and ? and logg between ? and ?' % modelName, gridLimits)
       
       
        
        return result.fetchall()
       
        
        
                                        
            
            
    def __getLevels(self, data, point, level=1):
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
        
        offset = numpy.array(data) - point
        
        # If there is an exact point that we want, then we don't want to interpolate at all        
        if 0.0 in offset: return [point]
        
        # we want level points on either side
        
        # split into positive and negative first
        
        pos = filter(lambda x: x > 0, offset)
        neg = filter(lambda x: x < 0, offset)

        # We may have duplicates of the same value, which is screwy with levels

        posUnique = numpy.unique(pos)
        negUnique = numpy.unique(neg)

        neighbours = numpy.array(list(posUnique)[0:level] + list(negUnique)[-level:])
        neighbours += point
        
        # May not be necessary
        neighbours.sort()
        
        return neighbours
         
        
        
            
            
    def __readDeck(self, filename, line=0, number=1):
        """
        
        Reads a filename beginning at the line <line> and returns <number>
        decks as CassiniKuruzModel() classes
        
        """
    
            
   
    def __grep(self, pattern, fileObject):
        """
        
        Performs the equivalent of a grep -n on a filename
        
        """
        
        r = []
        for number, line in enumerate(fileObject):
            if re.search(pattern, line):
                r.append((number, line))
        return r
            

            
if __name__ == "__main__":
    t = pyCasKur('../kurucz_models/')
    found = t.getNearestNeighbours(FeH=-0.25, logg=3.1, Teff=8100., level=1)
            
            
            
    
        
        
            
            
        