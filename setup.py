#!/usr/bin/env python

from distutils.core import setup
import setuptools

try: # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError: # Python 2.x
    from distutils.command.build_py import build_py


setup(name='atmosphy',
      version='1.0b1',
      description='Stellar atmosphere models in Python',
      author='Wolfgang Kerzendorf and Andy Casey',
      author_email='wkerzendorf@mso.anu.edu.au, \
        acasey@mso.anu.edu.au',
      url='',
      packages = ['atmosphy'],
      package_dir = {'atmosphy':'./'},
      cmdclass = {'build_py':build_py},
      data_files = [('conf.d', ['conf.d/atmosphy.schema', 'conf.d/config.ini'])],
      scripts=['scripts/atmosphy', 'scripts/atmosphy_getgrid'],
      install_requires = ['argparse>=1.1', 'scipy>=0.9.0rc5'],
      test_suite = 'nose.collector'
     )


