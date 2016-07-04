PYCODESTYLE_RUN := $(PYTHON_SRC:%=pycodestyle-run-%)

# The pep8 tool has been renamed to pycodestyle with its 2.0.0 release.
# Fallback to pep8 if it does not exist until distributions have caught up.
PYCODESTYLE_EXE := $(if $(shell pycodestyle --version 2> /dev/null),pycodestyle,pep8)

.PHONY: pycodestyle $(PYCODESTYLE_RUN)

pycodestyle: $(PYCODESTYLE_RUN)

$(PYCODESTYLE_RUN): pycodestyle-run-% : %
	$(PYCODESTYLE_EXE) $<
