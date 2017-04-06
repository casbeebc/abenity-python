#!/usr/bin/env python

from setuptools import setup

setup(
    name='abenity-python',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',

    description='Abenity API client',
    long_description=open('README.md', 'r').read(),

    # The project's main homepage.
    url='https://github.com/casbeebc/abenity-python',

    # Author details
    author='Brett Casbeer',
    author_email='brett.casbeer@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
)
