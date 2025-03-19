.PHONY: *

VENV=/opt/python_venvs/articles_api
PYTHON=$(VENV)/bin/python3
PIP=$(VENV)/bin/pip

DEPLOY_HOST := 93.123.95.160
SSH_PORT := 2122
APP_PORT := 5045
DOCKER_TAG := latest
DOCKER_IMAGE := articles_api
USERNAME := dmitriy


# ================== LOCAL WORKSPACE SETUP ==================
venv:
	~/.pyenv/versions/3.9.17/bin/python -m venv $(VENV)
	@echo 'Path to Python executable $(shell pwd)/$(PYTHON)'

.PHONY: install
install: venv
	@echo "=== Installing common dependencies ==="
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	curl -fsSL https://ollama.com/install.sh | sh

.PHONY: download_model
download_model:
	/usr/local/bin/ollama pull llama3
	/usr/local/bin/ollama pull bge-m3


# ================== RUN API SERVICE ==================
.PHONY: run_app
run_app:
	$(PYTHON) -m uvicorn app:create_app --host='0.0.0.0' --port=$(APP_PORT) --root-path /


# ================== RUN TESTS ==================
.PHONY: run_unit_tests
run_unit_tests:
	PYTHONPATH=. $(VENV)/bin/pytest tests/unit/

.PHONY: run_integration_tests
run_integration_tests:
	PYTHONPATH=. $(VENV)/bin/pytest tests/integration/

.PHONY: run_all_tests
run_all_tests:
	make run_unit_tests
	make run_integration_tests

.PHONY: generate_coverage_report
generate_coverage_report:
	PYTHONPATH=. pytest --cov=src --cov-report html  tests/

.PHONY: lint
lint:
	PYTHONPATH=. tox


# ================== DOCKER SETUP ==================
.PHONY: build
build:
	docker build -f Dockerfile . -t $(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: docker_run
docker_run:
	docker run -p $(APP_PORT):$(APP_PORT) -d --name goa $(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: install_c_libs
install_c_libs:
	apt-get update && apt-get install -y --no-install-recommends gcc ffmpeg libsm6 libxext6


# ================== AUTOMATIC SETUP ==================
.PHONY: deploy
deploy:
	ansible-playbook -i deploy/ansible/inventory.ini  deploy/ansible/deploy.yml \
		-e host=$(DEPLOY_HOST) \
		-e docker_image=$(DOCKER_IMAGE) \
		-e docker_tag=$(DOCKER_TAG) \
		-e docker_registry_user=$(CI_REGISTRY_USER) \
		-e docker_registry_password=$(CI_REGISTRY_PASSWORD) \
		-e docker_registry=$(CI_REGISTRY) \

.PHONY: destroy
destroy:
	ansible-playbook -i deploy/ansible/inventory.ini deploy/ansible/destroy.yml \
		-e host=$(DEPLOY_HOST)
