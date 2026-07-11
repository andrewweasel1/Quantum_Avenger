PYTHON ?= python3
export PYTHONPATH := $(CURDIR)

.PHONY: install lint test coverage docker compose-up

install:
	$(PYTHON) -m pip install -r new_pipeline/requirements.txt -r new_pipeline/requirements-dev.txt -r new_pipeline/requirements-api.txt

lint:
	ruff check new_pipeline

test:
	$(PYTHON) -m pytest new_pipeline/tests

coverage:
	NUMBA_DISABLE_JIT=1 $(PYTHON) -m pytest new_pipeline/tests --cov=new_pipeline --cov-report=term-missing --cov-fail-under=85

docker:
	docker build -f new_pipeline/hardening/docker/Dockerfile.app -t quantum-avenger-app .
	docker build -f new_pipeline/hardening/docker/Dockerfile.mcp -t quantum-avenger-mcp .

compose-up:
	docker compose -f new_pipeline/hardening/docker/docker-compose.yml up --build
