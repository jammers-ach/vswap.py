#!/usr/bin/env python
from setuptools import setup

setup(name='vswap',
      version='1.0',
      description='',
      author='jammers',
      author_email='jammers@gmail.com',
      url='https://github.com/jammers-ach/vswap.py',
      packages=['vswap',],
      install_requires=['pytest', 'numpy', 'Pillow', 'wave',
                        'pyopl'],
      dependency_links=[
          'https://github.com/adambiser/pyopl/archive/master.zip#egg=pyopl'
      ]
     )
