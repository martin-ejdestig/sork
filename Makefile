.DEFAULT_GOAL := all

PYTHON_SRC := $(shell find . -name "*.py" -printf "%P\n")

include makeinc/pycodestyle.mk
include makeinc/pylint.mk

.PHONY: all check unittest

all:

check: pycodestyle pylint

unittest:
	@python -m unittest discover
