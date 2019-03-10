.DEFAULT_GOAL := all

include makeinc/mypy.mk
include makeinc/pycodestyle.mk
include makeinc/pylint.mk

.PHONY: all check test

all:

check: mypy pycodestyle pylint

test:
	@python3 -m unittest discover
