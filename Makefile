## pytermor       ## ANSI formatted terminal output library
## (C) 2022       ## A. Shavykin <0.delameter@gmail.com>
##----------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test

PROJECT_NAME = pytermor

include .env.dist
-include .env
export
VERSION ?= 0.0.0

## Common commands

BOLD   := $(shell tput -Txterm bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^##\s*([^#]+)#*\s*(.*)/${YELLOW}\1${RESET}#\2/' -e 's/(.+):(#|\s)+(.+)/##   ${GREEN}\1${RESET}#\3/' | column -t -s '#'

cleanup:
	rm -f -v dist/* ${PROJECT_NAME}.egg-info/*

prepare:
	python3 -m pip install --upgrade build twine

test: ## Run tests
	PYTHONPATH=${PWD} python3 -s -m unittest -v

set-version: ## Set new package version
	@echo "Current version: ${YELLOW}${VERSION}${RESET}"
	read -p "New version (press enter to keep current): " VERSION
	if [ -z $$VERSION ] ; then echo "No changes" && return 0 ; fi
	if [ ! -f .env ] ; then cp -u .env.dist .env ; fi
	sed -E -i "s/^VERSION.+/VERSION=$$VERSION/" .env
	sed -E -i "s/^version.+/version = $$VERSION/" setup.cfg
	echo "Updated version: ${GREEN}$$VERSION${RESET}"

build: ## Build module
build: cleanup
	sed -E -i "s/^VERSION.+/VERSION=$$VERSION/" .env.dist
	python3 -m build
	mv -f ${PROJECT_NAME}/${PROJECT_NAME}.egg-info .

generate-readme: ## Generate README file
	PYTHONPATH=${PWD} python3 -s dev/readme/generate.py -v

generate-thumbs: ## Generate README examples' thumbnails
	PYTHONPATH=${PWD} python3 -s dev/readme/generate_thumbs.py -v

## Test repository

upload-dev: ## Upload module to test repository
	python3 -m twine upload --repository testpypi dist/* -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD}

install-dev: ## Install module from test repository
	pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME}-delameter==${VERSION}

## Primary repository

upload: ## Upload module
	python3 -m twine upload dist/* -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} --verbose

install: ## Install module
	pip install ${PROJECT_NAME}==${VERSION}

##