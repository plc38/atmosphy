#!/usr/bin/env python

from distutils.core import setup

try: # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError: # Python 2.x
    from distutils.command.build_py import build_py


setup(name='atmosphy',
      version='0.1',
      description='Stellar atmosphere models in Python',
      author='Wolfgang Kerzendorf and Andy Casey',
      author_email='wkerzendorf@mso.anu.edu.au, \
        acasey@mso.anu.edu.au',
      url='',
      packages = ['atmosphy'],
      cmdclass = {'build_py':build_py},
      data_files = [('~/.atmosphy', 'conf.d')],
      install_requires = ['http://pypi.python.org/packages/source/a/argparse/argparse-1.1.zip#md5=087399b73047fa5a6482037411ddc968']
     )


