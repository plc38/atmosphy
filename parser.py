

def getDBPath():
	return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf.d','pycaskur.db3')
    

     
    
    
        
        
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
            
            
            
    
        
        
            
            
        