.ONESHELL:

default: install

install:
	echo "hello"
	virtualenv -p python3.6 venv
	. venv/bin/activate
	pip install .
	subscribie init
	subscribie migrate
	pytest

clean:
	rm -rf venv
	find -iname "*.pyc" -delete

