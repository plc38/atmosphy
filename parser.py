
import glob
import os
import scipy



class pyCasKur():


    def __init__(self, folder=os.getcwd() + '/'):
    
        self.folder = folder
        
        
        return None
        
        
    
    def getNearestNeighbours(self, FeH=None, Teff=None, logg=None, level=1):
    
        """
        
        Finds the nearest neighbours from a directory of Kurucz model files.
        
        Parameters:
        ===========
        
        FeH : float
                The metallicity ([Fe/H]) of the star you plan to interpolate for.
                
        Teff : float
                The effective temperature (Teff) of the star you plan to interpolate for.
        
        logg : float
                The surface gravity (log g) of the star you plan to interpolate for.
    
        """
        
        
        # This assumes that the Cas-Kuz models are in the appropriate format for parsing between
        # That is:
        
        # a[p|m][0-9]{2}k[0-9]{1,}.dat

        
        models = glob.glob(self.folder + 'a[m|p]*k[0-9].dat')

        if (1 > level):
            raise ValueError, 'level must be a positive integer'


        # point must be specified in [Fe/H], Teff, Gravity (for computational efficiency)
    

        
        # We want to find all the FeH points from the filenames
        
        FeH_available = [None] * len(models)
        modelFiles = [None] * len(models)
        
        for i, model in enumerate(models):
            modelFiles[i] = model
            
            model = os.path.basename(model)
            
            FeH_available[i] = eval(model[1:4].replace('m', '-').replace('p', '+'))/10.
        
        
        
        
        # We want to grep through all the files and get the possible points for the grid.
        # Then we will use a spatial KDD Tree to find the N closest neighbours.        
                    
        # Generate our grid, which will be [FeH, Teff, logg]
        grid = []
        
        # Look in each of our model files and grab the Teff's and logg's
        for FeH_point, modelFile in zip(FeH_available, modelFiles):

            
            data = file(modelFile, 'r')
            matches = self.__grep('TEFF\s+[0-9.]+\s+GRAVITY\s+[0-9.]+\s+LTE', data)

            for patternMatch in matches:
                number, line = patternMatch
                line = re.split('\s+', line)
                
                grid.append([FeH_point, float(line[1]), float(line[3])])

        
        # Find the nearest N levels of indexedFeHs
        FeH_grid = self.__getLevels(FeH_available, FeH, level=level)

        # Find the Teff available for our FeH possibilites
        Teff_available = [point[1] for point in grid if point[0] in FeH_grid]

        # Find the nearest N levels of Teff_available to Teff
        Teff_grid = self.__getLevels(Teff_available, Teff, level=level)
        
        # Find the logg available for our FeH and Teff possibilities
        logg_available = [point[2] for point in grid if point[0] in FeH_grid and point[1] in Teff_grid]
        
        # Find the nearest N levels of logg_available to logg
        logg_grid = self.__getLevels(logg_available, logg, level=level)

    
        # Generate the sql statement

        query = """select * from table where feh    between '%f' and '%f' 
                                         and teff   between '%f' and '%f'
                                         and logg   between '%f' and '%f'""" % (min(FeH_grid), max(FeH_grid), min(Teff_grid), max(Teff_grid), min(logg_grid), max(logg_grid))
        
        return query
                                        
            
            
    def __getLevels(self, data, point, level=1):
        """
        
        Returns closest neighbours on either side of the point provided..

        Parameters:
        ===========
        
        data : array
                The data points used to find neighbours from.
                
        point : float
                The point used to look for neighbours.
                
        level : integer, optional
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
    found = t.getNearestNeighbours(-0.25, logg=3.1, Teff=8100., level=2)
            
            
            
        
        
        
            
            
        