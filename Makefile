.PHONY: test lint clean dev install dist run help

help:
	@echo
	@echo "  test       run tests & linter"
	@echo "  lint       check style"
	@echo "  clean      remove build and python file artifacts"
	@echo "  dev        install in development mode"
	@echo "  install"
	@echo "  run        run checkout_server for development"
	@echo "  help       print this message"
	@echo

test: lint
	py.test --strict tests

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf .coverage dist build htmlcov

coverage:
	coverage run --source checkout_server setup.py test
	coverage report -m
	coverage html
	@echo "coverage report: file://`pwd`/htmlcov/index.html"

lint:
	flake8 checkout_server tests

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

dev: clean
	pip install -e '.[dev]'

install: clean
	python setup.py install

run: clean
	FLASK_APP=checkout_server.app FLASK_ENV=development flask run --port 7001
