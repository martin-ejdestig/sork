.DEFAULT_GOAL := all

include makeinc/mypy.mk
include makeinc/pycodestyle.mk
include makeinc/pylint.mk

.PHONY: all check unittest

all:

check: mypy pycodestyle pylint

unittest:
	@python3 -m unittest discover
