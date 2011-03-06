#!/usr/bin/env python

from distutils.core import setup


try: # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError: # Python 2.x
    from distutils.command.build_py import build_py


setup(name='atmosphy',
      version='1.0b2',
      description='Stellar atmosphere models in Python',
      author='Wolfgang Kerzendorf and Andy Casey',
      author_email='wkerzendorf@mso.anu.edu.au, \
        acasey@mso.anu.edu.au',
      url='',
      packages = ['atmosphy'],
      package_dir = {'atmosphy':'.'},
      package_data = {'atmosphy':['conf.d/atmosphy.schema',]},
      cmdclass = {'build_py':build_py},
      scripts=['scripts/atmosphy', 'scripts/atmosphy_getgrid', 'scripts/atmosphy_stromlo'],
      install_requires = ['argparse>=1.1'],#, 'scipy>=0.9.0rc5'],
      test_suite = 'nose.collector'
     )


