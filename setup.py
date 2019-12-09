from setuptools import setup, find_packages
import os
setup(name='dutchgic',
      version='1.0',
      description='GIC calculation in Dutch powergrid',
      url='https://github.com/outfrenk/Dutch_GIC',
      author='Frenk Out',
      author_email='outfrenk@gmail.com',
      license='MIT',
      packages=find_packages(include=['Dutch_GIC'],exclude=['Tests']),
      install_requires=['pandas','numpy','scipy','matplotlib'],
      tests_require=['pytest'],
      )