# Responsys Interact API python client #

A python library providing access to the Responsys Interact API.

## Install ##

Via pypi:

	pip install responsys

Via source package:

	cd responsys/
	pip install .

## Usage ##

The [InteractClient](./responsys/client.py) provides the methods needed to work with
the Interact API:

	>>> from responsys.client import InteractClient
	>>> client = InteractClient(username, password, pod)
	>>> client.connect()
	>>> client.merge_list_members(interact_object, records, merge_rules)
	>>> client.disconnect()

Using the client class as a context manager will automatically connect using the credentials
provided, and disconnect upon context exit:

	>>> with InteractClient(username, password, pod) as client:
	...     client.merge_list_members(interact_object, records, merge_rules)

Since responsys limits the number of active sessions per account, this can help ensure you
don't leave unused connections open.

## Development/Testing ##

Tests can be run via setuptools:

	python setup.py nosetests

Installing requirements for development environment can be accomplished via pip:

	pip install -r requirements.txt

Testing within a dev environment can be accomplished via ```nosetests```.

## Acknowledgements ##

This library was developed while working for the fine folks at
[udemy.com](http://www.udemy.com/about).

## Legal ##

This code is neither officially supported nor endorsed by Udemy.com, Oracle, Responsys, or any
related entites.

[License](./LICENSE)
