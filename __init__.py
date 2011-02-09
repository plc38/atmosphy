import os
from shutil import copyfile


# Generate the once-off ~/.atmosphy directory
atmosphyUserPath = os.path.expanduser('~/.atmosphy')
if not os.path.exists(atmosphyUserPath):
    os.makedirs(atmosphyUserPath)

# Copy the config file into the user home directory
if not os.path.exists(os.path.join(atmosphyUserPath, 'config.ini')):
    copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'conf.d', 'config.ini'),
             os.path.join(atmosphyUserPath, 'config.ini'))
    
