PYLINT_RUN := $(PYTHON_SRC:%=pylint-run-%)
PYLINT_FLAGS ?= --persistent=n --reports=n --score=n --msg-template="{path}:{line}: {msg} [{symbol}]"

# Some distributions ship Pylint for Python 3 as pylint3 or pylint-3.
PYLINT_EXE := $(firstword $(foreach c,pylint3 pylint-3 pylint,\
                            $(if $(shell $c --version 2> /dev/null),$c)))

.PHONY: pylint $(PYLINT_RUN)

pylint: $(PYLINT_RUN)

$(PYLINT_RUN): pylint-run-% : %
	@echo pylint $<
	@$(PYLINT_EXE) $(PYLINT_FLAGS) $< 2>&1 | grep -v "^\*\+ Module " || true
