import os
from shutil import copyfile

# Generate the once-off ~/.atmosphy directory
atmosphyUserPath = os.path.expanduser('~/.atmosphy')
if not os.path.exists(atmosphyUserPath):
    os.makedir(atmosphyUserPath)

# Copy the config file into the user home directory
if not os.path.exists(os.path.join(atmosphyUserPath, 'conf.d')):
    copyfile(os.path.join(os.path.realpath(__file__), 'conf.d'), os.path.join(atmosphyUserPath, 'conf.d'))
    
