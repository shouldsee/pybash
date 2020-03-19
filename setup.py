#!/usr/bin/env python
#from setuptools import setup

# from distutils.core import setup
try:
	from setuptools import setup, find_packages
except Exception as e:
	print('installing pybash: setuptools not found'
		'\nsee https://stackoverflow.com/questions/14426491/python-3-importerror-no-module-named-setuptools')
	raise e
import sys
assert sys.version_info >= (3,4),('Requires python>=3.4, found python==%s'%('.'.join([str(x) for x in sys.version_info[:3]])))

config = dict(
	name='pybash',
	version = '0.0.3', ### change in __init__.py in sync
	# package_dir={"": "."},
    packages=['.'],
	include_package_data=True,
	license='MIT',
	author='Feng Geng',
	author_email='shouldsee.gem@gmail.com',
	long_description=open('README.md').read(),
	# python_requires = '>=3.6',
	classifiers = [
	'Programming Language :: Python :: 3.5',
	'Programming Language :: Python :: 3.7',
	],
	install_requires=[
		x.strip() for x in open("requirements.txt","r")
        	if x.strip() and not x.strip().startswith("#")
	],
    entry_points={
        "console_scripts": [
            "pybash=pybash:main",
            ]},	
)

if __name__ == '__main__':
	setup(**config)
