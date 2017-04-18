#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', '-s', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='abenity',
    packages=['abenity'],
    version='0.0.1',

    description='Abenity API client',
    long_description='A Python library for using the Abenity API.',
    url='https://github.com/casbeebc/abenity-python',
    author='Brett Casbeer',
    author_email='brett.casbeer@gmail.com',
    license='MIT',
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    setup_requires=['setuptools>=17.1'],
    install_requires=['requests==2.13.0', 'pycryptodome==3.4.5'],
    extras_require={'testing': ['pytest']},
    tests_require=['pytest'],
)
