.ONESHELL:

default: install

install:
	echo "hello"
	virtualenv -p python3.6 venv
	. venv/bin/activate
	pip install .
	pytest

clean:
	rm -rf venv
	find -iname "*.pyc" -delete

