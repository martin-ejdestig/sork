.DEFAULT_GOAL := all

PYTHON_SRC := $(shell find . -name "*.py" -printf "%P\n")

include makeinc/mypy.mk
include makeinc/pycodestyle.mk
include makeinc/pylint.mk

.PHONY: all check unittest

all:

check: mypy pycodestyle pylint

unittest:
	@python3 -m unittest discover
