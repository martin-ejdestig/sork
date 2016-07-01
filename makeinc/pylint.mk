PYLINT_RUN := $(PYTHON_SRC:%=pylint-run-%)
PYLINT_FLAGS ?= --reports=n --msg-template="{path}:{line}: {msg} [{symbol}]"

.PHONY: pylint $(PYLINT_RUN)

pylint: $(PYLINT_RUN)

$(PYLINT_RUN): pylint-run-% : %
	@echo pylint $<
	@pylint $(PYLINT_FLAGS) $< 2>&1 | grep -v "^\*\+ Module " || true
