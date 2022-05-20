## pytermor       ## ANSI formatted terminal output toolset
## (C) 2022       ## A. Shavykin <0.delameter@gmail.com>
##----------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test

PROJECT_NAME = pytermor

include .env.dist
-include .env
export
VERSION ?= 0.0.0

BOLD   := $(shell tput -Txterm bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)


## Common commands

help:   ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^##\s*([^#]+)#*\s*(.*)/${YELLOW}\1${RESET}#\2/' -e 's/(.+):(#|\s)+(.+)/##   ${GREEN}\1${RESET}#\3/' | column -t -s '#'

cleanup:
	rm -f -v dist/* ${PROJECT_NAME}.egg-info/*

prepare:  ## Init environemnt
	python3 -m pip install --upgrade build twine
	python3 -m venv venv
	. venv/bin/activate
	pip3 install -r requirements-dev.txt

test: ## Run tests
	. venv/bin/activate
	PYTHONPATH=${PWD} python3 -m pytest tests

test-verbose: ## Run tests with detailed output
	. venv/bin/activate
	PYTHONPATH=${PWD} python3 -m pytest tests -v

test-debug: ## Run tests with VERY detailed output
	. venv/bin/activate
	PYTHONPATH=${PWD} python3 -m pytest tests -v --log-cli-level=DEBUG

coverage: ## Run coverage tool
	. venv/bin/activate
	PYTHONPATH=${PWD} coverage run tests -vv
	coverage report

set-version: ## Set new package version
	@echo "Current version: ${YELLOW}${VERSION}${RESET}"
	read -p "New version (press enter to keep current): " VERSION
	if [ -z $$VERSION ] ; then echo "No changes" && return 0 ; fi
	if [ ! -f .env ] ; then cp -u .env.dist .env ; fi
	sed -E -i "s/^VERSION.+/VERSION=$$VERSION/" .env .env.dist
	sed -E -i "s/^version.+/version = $$VERSION/" setup.cfg
	sed -E -i "s/^__version__.+/__version__ = '$$VERSION'/" ${PROJECT_NAME}/_version.py
	echo "Updated version: ${GREEN}$$VERSION${RESET}"

update-readme: ## Generate and rewrite README
	. venv/bin/activate
	PYTHONPATH=${PWD} python3 -s dev/readme/update_readme.py


## Test repository

build-dev: ## Build module with dev name
build-dev: cleanup
	sed -E -i "s/^name.+/name = ${PROJECT_NAME}-delameter/" setup.cfg
	python3 -m build
	sed -E -i "s/^name.+/name = ${PROJECT_NAME}/" setup.cfg

upload-dev: ## Upload module to dev repository
	python3 -m twine upload --repository testpypi dist/* -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD_DEV} --verbose

install-dev: ## Install module from dev repository
	pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME}-delameter==${VERSION}


## Primary repository

build: ## Build module
build: cleanup
	python3 -m build

upload: ## Upload module
	python3 -m twine upload dist/* -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} --verbose

install: ## Install module
	pip install ${PROJECT_NAME}==${VERSION}


## Documentation

build-docs-toc: ## Erase and recreate docs table of contents
	rm docs/*.rst
	sphinx-apidoc --force --separate --module-first --tocfile index --output-dir docs pytermor

build-docs: ## Build documentation
	rm -rf docs/_build
	sphinx-build -aEn docs docs/_build -b html
##
