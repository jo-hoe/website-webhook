include help.mk

# get content of .env as environment variables
include .env
export

.DEFAULT_GOAL := start

ROOT_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
IMAGE_NAME := "website-webhook"
IMAGE_VERSION := "1.0.0"

.PHONY: pull
pull:
	@git -C ${ROOT_DIR} pull

.PHONY: update
update: pull ## pulls git repo and installs all dependencies
	${ROOT_DIR}.venv/Scripts/pip install -r ${ROOT_DIR}requirements.txt

.PHONY: start-cluster
start-cluster:
	@k3d cluster create --config ${ROOT_DIR}k3d/clusterconfig.yaml -v '${ROOT_DIR}k3d/cache/:/tmp'
	@helm install go-mail-service --set service.port=$(API_PORT) \
				--set defaultSenderMailAddress=$(DEFAULT_FROM_ADDRESS) \
				--set defaultSenderName=$(DEFAULT_FROM_NAME) \
				--set sendgrid.apiKey=$(SENDGRID_API_KEY) \
				https://github.com/jo-hoe/go-mail-service/releases/download/go-mail-service-0.0.6/go-mail-service-0.0.6.tgz
	@kubectl apply -f ${ROOT_DIR}k3d/cronjob.yaml

.PHONY: start-k3d
start-k3d: start-cluster push-to-registry ## starts k3d and deploys local image

.PHONY: stop-k3d
stop-k3d: ## stop K3d
	@k3d cluster delete --config ${ROOT_DIR}k3d/clusterconfig.yaml

.PHONY: restart-k3d
restart-k3d: stop-k3d start-k3d ## restart k3d

.PHONY: push-to-registry
push-to-registry: ## build and push docker image to local registry
	@docker build -f ${ROOT_DIR}Dockerfile . -t ${IMAGE_NAME}
	@docker tag ${IMAGE_NAME} localhost:5000/${IMAGE_NAME}:${IMAGE_VERSION}
	@docker push localhost:5000/${IMAGE_NAME}:${IMAGE_VERSION}

.PHONY: start
start: ## start in docker container
	@docker build . -t "${IMAGE_NAME}"
	@docker run --rm -v ${ROOT_DIR}state\:/app/state/ ${IMAGE_NAME}

.PHONY: start-exec
start-exec: ## start in docker container and exec into it
	@docker build . -t "${IMAGE_NAME}"
	@docker run --rm -it --env-file ${ROOT_DIR}.env --entrypoint "bash" -v ${ROOT_DIR}state\:/app/state/ ${IMAGE_NAME}