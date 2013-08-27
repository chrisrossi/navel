from setuptools import setup
from setuptools import find_packages

VERSION = '0.1dev'

requires = [
    'substanced',
    'slugger',
]
tests_require = requires + []

testing_extras = tests_require + ['nose', 'coverage']
doc_extras = ['Sphinx']

setup(name='navel',
      version=VERSION,
      description='Blog package for use with Substance D',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_require,
      extras_require={
          'testing': testing_extras,
      },
      test_suite="navel.tests")
