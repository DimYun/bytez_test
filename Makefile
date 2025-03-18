.PHONY: *

VENV=/opt/python_venvs/articles_api
PYTHON=$(VENV)/bin/python3
PIP=$(VENV)/bin/pip

DEPLOY_HOST := 93.123.95.160
SSH_PORT := 2122
APP_PORT := 5045
DOCKER_TAG := latest
DOCKER_IMAGE := articles_api
#DVC_REMOTE_NAME := dvc_models_goa
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
	/usr/local/bin/ollama pull llama3
	/usr/local/bin/ollama pull bge-m3


# ================== LOCAL WORKSPACE SETUP ==================
.PHONY: run_app
run_app:
	$(PYTHON) -m uvicorn app:create_app --host='0.0.0.0' --port=$(APP_PORT) --root-path /


# ================== LOCAL WORKSPACE SETUP ==================
.PHONY: download_model
download_model:
	dvc remote modify --local $(DVC_REMOTE_NAME) keyfile ~/.ssh/id_rsa
	dvc pull

.PHONY: download_model_manual
download_model_manual:
	dvc remote modify --local $(DVC_REMOTE_NAME) ask_passphrase true
	dvc pull

.PHONY: run_unit_tests
run_unit_tests:
	PYTHONPATH=. pytest tests/unit/

.PHONY: run_integration_tests
run_integration_tests:
	PYTHONPATH=. pytest tests/integration/

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

.PHONY: build
build:
	docker build -f Dockerfile . -t $(DOCKER_IMAGE):$(DOCKER_TAG)

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

.PHONY: install_dvc
install_dvc:
	pip install dvc[ssh]==3.33.2


.PHONY: init_dvc
init_dvc:
	dvc init --no-scm
	dvc remote add --default $(DVC_REMOTE_NAME) ssh://$(DEPLOY_HOST):$(SSH_PORT)/home/$(USERNAME)/$(DVC_REMOTE_NAME)
	dvc remote modify $(DVC_REMOTE_NAME) user $(USERNAME)
	dvc config cache.type hardlink,symlink

.PHONY: install_c_libs
install_c_libs:
	apt-get update && apt-get install -y --no-install-recommends gcc ffmpeg libsm6 libxext6

.PHONY: docker_run
docker_run:
	docker run -p $(APP_PORT):$(APP_PORT) -d --name goa $(DOCKER_IMAGE):$(DOCKER_TAG)
