import os
from shutil import copyfile
#import initialize
import logging

atmosphyUserPath = os.path.expanduser('~/.atmosphy')
moduleDir = os.path.dirname(os.path.realpath(__file__))

# Generate the once-off ~/.atmosphy directory

if not os.path.exists(atmosphyUserPath):
    os.makedirs(atmosphyUserPath)
    
#Creating a atmosphy.db3
if not os.path.exists(os.path.join(atmosphyUserPath, 'atmosphy.db3')):
    import sqlite3
    conn = sqlite3.connect(os.path.join(atmosphyUserPath, 'atmosphy.db3'))
    conn.executescript(file(os.path.join(moduleDir, 'conf.d', 'atmosphy.schema')).read())
    conn.commit()
    conn.close()
