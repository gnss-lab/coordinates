from setuptools import setup, find_packages
from codecs import open
from os import path

import coordinates

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='coordinates',

    description='Tools to manipulate cooridnates for GISMO project',
    long_description=long_description,

    version=coordinates.__version__,

    url='https://github.com/gnss-lab/coordinates',

    author=coordinates.__author__,
    author_email=coordinates.__email__,

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',

        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
    ],

    keywords='ionosphere gnss coordinates development',

    packages=find_packages(exclude=['docs', 'tests']),

    install_requires=[],

    python_requires='>=3',

    extras_require={
        'test': ['pytest'],
    },
)
