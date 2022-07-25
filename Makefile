## pytermor       ## ANSI formatted terminal output toolset
## (c) 2022       ## A. Shavykin <0.delameter@gmail.com>
##----------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test docs

PROJECT_NAME = pytermor

include .env.dist
-include .env
export
VERSION ?= 0.0.0

BOLD   := $(shell tput -Txterm bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
INV    := $(shell tput -Txterm rev)
RESET  := $(shell tput -Txterm sgr0)
SEPU   := $(shell printf "┌%48s┐" "" | sed 's/ /─/g')
SEPD   := $(shell printf "└%48s┘" "" | sed 's/ /─/g')
SEPL   := $(shell printf "│ ")
SEPR   := $(shell printf " │")
log_success = (echo ${SEPU}; printf "%-6s%-36sOK\n" $1 | tr '\t' ' ' | sed -Ee "s/(\s*\S+\s+)(\S+\s+)(\S+)/${SEPL}\x01[m\2\x01[32m\1\x01[32;1;7m \3 \x01[m${SEPR}/" | tr '\001' '\033'; echo ${SEPD})


## Common commands

help:   ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^(##)\s*([^#]+)#*\s*(.*)/\1${YELLOW}\2${RESET}#\3/' -e 's/(.+):(#|\s)+(.+)/##   ${GREEN}\1${RESET}#\3/' | column -t -s '#'

all:   ## Prepare, run tests, generate docs and reports, build module
all: prepare prepare-pdf test doctest coverage docs-all build

prepare:  ## Prepare environment for module building
	python3 -m pip install --upgrade build twine
	python3 -m venv venv
	. venv/bin/activate
	pip3 install -r requirements-dev.txt

prepare-pdf:  ## Prepare environment for pdf rendering
	sudo apt install texlive-latex-recommended \
					 texlive-fonts-recommended \
					 texlive-latex-extra latexmk

set-version: ## Set new package version
	@echo "Current version: ${YELLOW}${VERSION}${RESET}"
	read -p "New version (press enter to keep current): " VERSION
	if [ -z $$VERSION ] ; then echo "No changes" && return 0 ; fi
	if [ ! -f .env ] ; then cp -u .env.dist .env ; fi
	sed -E -i "s/^VERSION.+/VERSION=$$VERSION/" .env .env.dist
	sed -E -i "s/^version.+/version = $$VERSION/" setup.cfg
	sed -E -i "s/^__version__.+/__version__ = '$$VERSION'/" ${PROJECT_NAME}/_version.py
	echo "Updated version: ${GREEN}$$VERSION${RESET}"

demolish-build:
	rm -f -v dist/* ${PROJECT_NAME}.egg-info/*


## Local testing

test: ## Run pytest
	. venv/bin/activate
	PYTHONPATH=`pwd` python3 -m pytest tests

test-verbose: ## Run pytest with detailed output
	. venv/bin/activate
	PYTHONPATH=`pwd` python3 -m pytest tests -v

test-debug: ## Run pytest with VERY detailed output
	. venv/bin/activate
	PYTHONPATH=`pwd` python3 -m pytest tests -v --log-cli-level=DEBUG

doctest: ## Run doctest
	. venv/bin/activate
	make -C docs doctest 2>&1 | grep -iEe 'failed example|summary' -A6 | sed -E -e 's/^\*+//' -e '/^\-/ d'

coverage: ## Run coverage and make a report
	rm -v coverage-report/*
	. venv/bin/activate
	PYTHONPATH=`pwd` coverage run tests -vv
	coverage report
	coverage html
	if [ -n $$DISPLAY ] ; then xdg-open coverage-report/index.html ; fi

#update-readme: # Generate and rewrite README
#	. venv/bin/activate
#	PYTHONPATH=`pwd` python3 -s dev/readme/update_readme.py


## Documentation

reinit-docs: ## Erase and reinit docs with auto table of contents
	rm -v docs/*.rst
	. venv/bin/activate
	sphinx-apidoc --force --separate --module-first --tocfile index --output-dir docs pytermor

demolish-docs:
	rm -rvf docs/_build

docs: ## Build HTML documentation
docs: demolish-docs
	. venv/bin/activate
	sphinx-build -aEn docs docs/_build -b html
	find docs/_build -type f -name '*.html' | sort | xargs -n1 grep -HnT ^ | sed s@^docs/_build/@@ > docs-build/pytermor.html.dump
	@if [ -n "${DISPLAY}" ] ; then xdg-open docs/_build/index.html ; fi

docs-pdf: ## Build PDF documentation
	. venv/bin/activate
	yes "" | make -C docs latexpdf  # twice for building pdf toc
	yes "" | make -C docs latexpdf  # @FIXME broken unicode
	mv docs/_build/latex/pytermor.pdf docs-build/pytermor.pdf
	@if [ -n "${DISPLAY}" ] ; then xdg-open docs-build/pytermor.pdf ; fi

docs-man: ## Build man pages
	. venv/bin/activate
	sed -i.bak -Ee 's/^.+<<<MAKE_DOCS_MAN<<</#&/' docs/conf.py
	make -C docs man || echo 'Generation failed'
	mv docs/conf.py.bak docs/conf.py
	mv docs/_build/man/pytermor.1 docs-build/pytermor.1

docs-all: ## Build documentation in all formats
docs-all: docs docs-pdf docs-man
	@echo
	@$(call log_success,$$(du -h docs-build/*)) | sed -E '1s/^(..).{7}/\1SUMMARY/'


## Dev repository

build-dev: ## Build module with dev project name
build-dev: demolish-build
	sed -E -i "s/^name.+/name = ${PROJECT_NAME}-delameter/" setup.cfg
	python3 -m build
	sed -E -i "s/^name.+/name = ${PROJECT_NAME}/" setup.cfg

upload-dev: ## Upload module to dev repository
	python3 -m twine upload --repository testpypi dist/* \
			-u ${PYPI_USERNAME} -p ${PYPI_PASSWORD_DEV} --verbose

install-dev: ## Install module from dev repository
	pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME}-delameter==${VERSION}


## Primary repository

build: ## Build module
build: demolish-build
	python3 -m build

upload: ## Upload module
	python3 -m twine upload dist/* -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} --verbose

install: ## Install module
	pip install ${PROJECT_NAME}==${VERSION}

##
