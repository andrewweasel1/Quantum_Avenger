PYTHON ?= python3
export PYTHONPATH := $(CURDIR)

.PHONY: install lint test coverage

install:
	$(PYTHON) -m pip install -r new_pipeline/requirements.txt -r new_pipeline/requirements-dev.txt "alpaca-py>=0.33"

lint:
	ruff check new_pipeline

test:
	$(PYTHON) -m pytest new_pipeline/tests

coverage:
	NUMBA_DISABLE_JIT=1 $(PYTHON) -m pytest new_pipeline/tests --cov=new_pipeline --cov-report=term-missing --cov-fail-under=85
