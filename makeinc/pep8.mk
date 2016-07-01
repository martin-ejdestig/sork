PEP8_RUN := $(PYTHON_SRC:%=pep8-run-%)

.PHONY: pep8 $(PEP8_RUN)

pep8: $(PEP8_RUN)

$(PEP8_RUN): pep8-run-% : %
	pep8 $<
