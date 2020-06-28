.ONESHELL:

default: install

install:
	virtualenv -p python3.6 venv
	. venv/bin/activate
	pip install .
	cp .env.example .env
	python -m pytest

clean:
	rm -rf venv
	find -iname "*.pyc" -delete

