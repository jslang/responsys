from setuptools import setup, find_packages
from os import path

project_dir = path.abspath(path.dirname(__file__))
with open(path.join(project_dir, 'README.md')) as f:
    long_description = f.read()

install_requires = (
    'suds-jurko'
)
tests_require = (
    'nose',
    'pinocchio',
    'mock',
)

setup(
    name='responsys',
    keywords='responsys interact client api',
    version='0.1.0',
    author='Jared Lang',
    author_email='kaptainlange@gmail.com',
    description='Python client library for the Responsys Interact API',
    long_description=long_description,
    packages=find_packages(),
    license='LICENSE',
    install_requires=install_requires,
    setup_requires=tests_require,
    tests_require=tests_require,
    test_suite='nose.collector',
)