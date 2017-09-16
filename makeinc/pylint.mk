PYLINT_JOBS_FLAG = $(filter -j%,$(MAKEFLAGS))
PYLINT_FLAGS ?= $(PYLINT_JOBS_FLAG) --persistent=n --reports=n --score=n --msg-template="{path}:{line}: {msg} [{symbol}]"

# Some distributions ship Pylint for Python 3 as pylint3 or pylint-3.
PYLINT_EXE := $(firstword $(foreach c,pylint3 pylint-3 pylint,\
                            $(if $(shell $c --version 2> /dev/null),$c)))

.PHONY: pylint

pylint:
	@echo $(PYLINT_EXE) sork
	@$(PYLINT_EXE) $(PYLINT_FLAGS) sork
