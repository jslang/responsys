from setuptools import setup, find_packages
from os import path

import responsys

project_dir = path.abspath(path.dirname(__file__))
with open(path.join(project_dir, 'README.md')) as f:
    long_description = f.read()

install_requires = (
    'suds-jurko'
)
tests_require = (
    'coverage',
    'mock',
    'nose',
    'pep8',
    'pinocchio',
    'pyflakes',
    'testtube',
)

setup(
    name=responsys.__name__,
    keywords=responsys.__keywords__,
    version=responsys.__version__,
    url='https://github.com/jslang/responsys',
    author='Jared Lang',
    description='Python client library for the Responsys Interact API',
    long_description=long_description,
    packages=find_packages(),
    license='GPLv2',
    install_requires=install_requires,
    setup_requires=tests_require,
    tests_require=tests_require,
    test_suite='nose.collector',
)
