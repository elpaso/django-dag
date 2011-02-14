#!/usr/bin/env python

import os
from distutils.core import setup

version = '1.1'

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Programming Language :: Python",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
    "Environment :: Web Environment",
    "Framework :: Django",
]

root_dir = os.path.dirname(__file__)
if not root_dir:
    root_dir = '.'
long_desc = open(root_dir + '/README').read()

setup(
    name='django-dag',
    version=version,
    url='https://github.com/elpaso/django-dag',
    author='Alessandro Pasotti',
    author_email='apasotti@gmail.com',
    license='GNU Affero General Public License v3',
    packages=['django_dag'],
    package_dir={'django_dag': 'django_dag'},
    #package_data={'dag': ['templates/admin/*.html']},
    description='Directed Acyclic Graph implementation for Django 1.0+',
    classifiers=classifiers,
    long_description=long_desc,
)
