#!/usr/bin/env python
from setuptools import setup
import sys, platform
from codecs import open


_PY3 = sys.version_info[0] == 3

def lines(text):
    """
    Returns each non-blank line in text enclosed in a list.
    See http://pypi.python.org/pypi/textdata for more sophisticated version.
    """
    return [l.strip() for l in text.strip().splitlines() if l.strip()]

system = str(sys.platform).lower()
impl = platform.python_implementation()

requires = ['six>=1.10',
            'options>=1.4.6',
            'say>=1.6.4',
            'pygments>=2.2.0',
            'mementos>=1.2.5',
            'textdata',
            'hjoin>=0.2.0',
            'ipython'
           ]

if 'darwin' in system:
    if impl != 'PyPy':
        requires += ['readline']

        # if iPython ran under PyPy, it'd require readline too
        # but on my system, readline fails to install under PyPy
        # thus this spot omission

elif 'win32' in system:
    requires += ['pyreadline']

setup(
    name='show',
    version='1.7.0',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Debug print statements, done right. E.g. show(x)',
    long_description=open('README.rst', encoding='utf-8').read(),
    url='https://bitbucket.org/jeunice/show',
    license='Apache License 2.0',
    packages=['show', 'show.astor'],
    setup_requires=[],
    install_requires=requires,
    tests_require=['tox', 'pytest', 'pytest-cov', 'coverage',
                   'six>=1.10', 'textdata', 'pexpect>=4.2.1'],
    test_suite="test",
    zip_safe=False,
    keywords='debug print display show',
    classifiers=lines("""
        Development Status :: 4 - Beta
        Operating System :: OS Independent
        License :: OSI Approved :: Apache Software License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: 3.4
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
        Framework :: IPython
        Environment :: Console
        Topic :: Software Development :: Libraries :: Python Modules
        Topic :: Printing
        Topic :: Software Development :: Debuggers
    """)
)
