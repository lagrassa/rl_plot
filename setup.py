from setuptools import setup

setup(
   name='rl_plot',
   version='1.0',
   description='RL plotting utilities',
   author='Alex LaGrassa',
   author_email='lagrassa@mit.edu',
   packages=['rl_plot'],  #same as name
   install_requires=['matplotlib', 'numpy'], #external packages as dependencies
   )
