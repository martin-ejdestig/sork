.DEFAULT_GOAL := all

PYTHON_SRC := $(shell find . -name "*.py" -printf "%P\n")

include makeinc/pycodestyle.mk
include makeinc/pylint.mk

.PHONY: all check mypy unittest

all:

check: mypy pycodestyle pylint

mypy:
	mypy --ignore-missing-imports -p sork

unittest:
	@python3 -m unittest discover
