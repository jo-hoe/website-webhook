include help.mk

# get root dir
ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
PYTHON_DIR := ${ROOT_DIR}.venv/Scripts/
IMAGE_NAME := "website-webhook"
IMAGE_VERSION := "latest"

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
	"${PYTHON_DIR}pip" list --not-required --format=freeze | grep -v "pip" > "${ROOT_DIR}requirements.txt"

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
start-k3d: start-cluster push-k3d ## run make `start-k3d` start k3d cluster and deploy local code with Redis
	@helm repo add bitnami https://charts.bitnami.com/bitnami
	@helm repo update
	@helm install redis bitnami/redis \
		--set auth.enabled=false \
		--set master.resources.requests.memory=32Mi \
		--set master.resources.limits.memory=32Mi \
		--set master.persistence.enabled=false \
		--set replica.replicaCount=0 \
		--set master.extraFlags[0]="--maxmemory 8mb" \
		--set master.extraFlags[1]="--maxmemory-policy allkeys-lru" \
		--set master.extraFlags[2]="--save \"\"" \
		--set master.extraFlags[3]="--appendonly no" \
		--set master.extraFlags[4]="--databases 1" \
		--set master.extraFlags[5]="--tcp-backlog 128" \
		--set master.extraFlags[6]="--maxclients 10" \
		--set master.extraFlags[7]="--hz 10"
	@helm install ${IMAGE_NAME} ${ROOT_DIR}charts/${IMAGE_NAME}  \
		--set image.repository=registry.localhost:5000/${IMAGE_NAME} --set image.tag=${IMAGE_VERSION} \
		--set storage.redis.host=redis-master \
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
