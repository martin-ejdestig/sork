# The pep8 tool has been renamed to pycodestyle with its 2.0.0 release.
# Fallback to pep8 if it does not exist until distributions have caught up.
# Some distributions ship pycodestyle for Python 3 as pycodestyle3 or pycodestyle-3.
PYCODESTYLE_EXE := $(firstword $(foreach c,pycodestyle3 pycodestyle-3 pycodestyle pep8,\
                                 $(if $(shell $c --version 2> /dev/null),$c)))

.PHONY: pycodestyle

pycodestyle:
	$(PYCODESTYLE_EXE) sork
