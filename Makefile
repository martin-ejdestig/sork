.DEFAULT_GOAL := all

PYTHON_SRC := $(shell find . -name "*.py" -printf "%P\n")

include makeinc/pep8.mk
include makeinc/pylint.mk

.PHONY: all check unittest

all:

check: pep8 pylint

unittest:
	@python -m unittest discover
