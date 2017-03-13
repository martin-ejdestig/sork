PYLINT_RUN := $(PYTHON_SRC:%=pylint-run-%)
PYLINT_FLAGS ?= --persistent=n --reports=n --score=n --msg-template="{path}:{line}: {msg} [{symbol}]"

# Some distributions ship Pylint for Python 3 as pylint3.
PYLINT_EXE := $(if $(shell pylint3 --version 2> /dev/null),pylint3,pylint)

.PHONY: pylint $(PYLINT_RUN)

pylint: $(PYLINT_RUN)

$(PYLINT_RUN): pylint-run-% : %
	@echo pylint $<
	@$(PYLINT_EXE) $(PYLINT_FLAGS) $< 2>&1 | grep -v "^\*\+ Module " || true
