.PHONY: test lint clean dev install dist run help

help:
	@echo
	@echo "  test       run tests"
	@echo "  lint       check style"
	@echo "  docs       generate docs"
	@echo "  clean      remove build and python file artifacts"
	@echo "  dev        install in development mode"
	@echo "  install"
	@echo "  run        run checkout_server for development"
	@echo "  help       print this message"
	@echo

test:
	py.test --strict tests

coverage:
	coverage run --source checkout_server setup.py test
	coverage report -m
	coverage html
	@echo "coverage report: file://`pwd`/htmlcov/index.html"

lint:
	flake8 checkout_server tests manage.py

docs:
	sphinx-apidoc -o docs/ checkout_server
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@echo "html docs: file://`pwd`/docs/_build/html/index.html"

clean:
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf .coverage dist build htmlcov

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

dev: clean
	pip install -r requirements_dev.txt
	python setup.py develop

install: clean
	python setup.py install

run: clean
	python manage.py runserver --port 7001
