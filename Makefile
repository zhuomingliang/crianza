PYPATH := PYTHONPATH=.:$$PYTHONPATH
CRIANZA := $(PYPATH) bin/crianza

# Tip: Try changing "python" to "pypy"
PYTHON := $(PYPATH) python

default: test

repl:
	@$(PYPATH) bin/crianza --repl

test:
	$(PYTHON) tests/crianza_test.py -v

test-genetic:
	$(PYTHON) examples/genetic/double-number.py
	$(PYTHON) examples/genetic/square-number.py

test-examples:
	$(CRIANZA) examples/fibonacci.source | head -15 | tr '\n' ' '; echo ""

check: test test-examples test-genetic

setup-test:
	python setup.py test

dist:
	rm -rf dist/
	WHEEL_TOOL=$(shell which wheel) python setup.py sdist bdist_wheel

publish: dist
	find dist -type f -exec gpg --detach-sign -a {} \;
	twine upload dist/*

tox:
	unset PYTHONPATH && tox

lint:
	pyflakes \
		crianza/*.py \
		tests/*.py \
		examples/genetic/*.py

clean:
	find . -name '*.pyc' -exec rm -f {} \;
