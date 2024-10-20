include help.mk

# get root dir
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
PYTHON_DIR := ${ROOT_DIR}.venv/Scripts/
IMAGE_NAME := "website-webhook"
IMAGE_VERSION := "2.1.0"

.DEFAULT_GOAL := start-docker

.PHONY: init
init: venv update ## init setup of project after checkout

.PHONY: venv
venv:
	@python -m venv ${ROOT_DIR}.venv

.PHONY: pull
pull:
	@git -C ${ROOT_DIR} pull

.PHONY: update
update: pull ## pulls git repo and installs all dependencies
	${PYTHON_DIR}pip install -r ${ROOT_DIR}requirements.txt

.PHONY: save-dependencies
save-dependencies: ## save current dependencies
	${PYTHON_DIR}pip freeze > ${ROOT_DIR}requirements.txt

.PHONY: test
test: ## run all tests
	${PYTHON_DIR}pytest $(ROOT_DIR)test/

.PHONY: start-docker
start-docker:
	@docker compose -f ${ROOT_DIR}compose.yaml up --build 

.PHONY: generate-helm-docs
generate-helm-docs: ## re-generates helm docs using docker
	@docker run --rm --volume "$(ROOT_DIR)charts:/helm-docs" jnorwood/helm-docs:latest

.PHONY: start-cluster
start-cluster: # starts k3d cluster and registry
	@k3d cluster create --config ${ROOT_DIR}k3d/clusterconfig.yaml

.PHONY: start-k3d
start-k3d: start-cluster push-k3d ## run make `start-k3d api_key=<your_api_key>` start k3d cluster and deploy local code
	@helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	@helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack
	@helm install ${IMAGE_NAME} ${ROOT_DIR}charts/${IMAGE_NAME}  \
		--set image.repository=registry.localhost:5000/${IMAGE_NAME} --set image.tag=${IMAGE_VERSION} \
		-f ${ROOT_DIR}dev/config.yaml

.PHONY: stop-k3d
stop-k3d: ## stop K3d
	@k3d cluster delete --config ${ROOT_DIR}k3d/clusterconfig.yaml

.PHONY: restart-k3d
restart-k3d: stop-k3d start-k3d ## restarts K3d
	
.PHONY: push-k3d
push-k3d: # build and push docker image to local registry
	@docker build -f ${ROOT_DIR}Dockerfile . -t ${IMAGE_NAME}
	@docker tag ${IMAGE_NAME} localhost:5000/${IMAGE_NAME}:${IMAGE_VERSION}
	@docker push localhost:5000/${IMAGE_NAME}:${IMAGE_VERSION}