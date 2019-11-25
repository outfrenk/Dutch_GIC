from setuptools import setup
import os
setup(name='dutchgic.py',
      version='1.0',
      description='GIC calculation in Dutch powergrid',
      url='https://github.com/outfrenk/Dutch_GIC',
      author='Frenk Out',
      author_email='outfrenk@gmail.com',
      license='MIT',
      packages=['Dutch_GIC'],
      install_requires=['numpy','re','pandas','logging','multiprocessing','threading','scipy','urllib','datetime','matplotlib'],
      zip_safe=False)
os.system('git clone https://github.com/greglucas/pySECS')
os.system('python setup.py install')