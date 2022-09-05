from setuptools import setup, find_packages


setup(
  name='half_geo',
  version='1.1.0',
  license='MIT',
  author="Izz Hafeez",
  author_email='izzhafeez@gmail.com',
  packages=find_packages('src'),
  package_dir={'': 'src'},
  url='https://github.com/mynameizzhafeez/geo',
  keywords='geospatial singapore',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  install_requires=[
      'pandas',
      'geopandas',
      'numpy',
      'shapely',
      'gsheets'
    ],

)