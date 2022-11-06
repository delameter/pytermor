## pytermor             ## ANSI formatted terminal output toolset
## (c) 2022             ## A. Shavykin <0.delameter@gmail.com>
##----------------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test docs

PROJECT_NAME = pytermor
PROJECT_NAME_PUBLIC = ${PROJECT_NAME}
PROJECT_NAME_PRIVATE = ${PROJECT_NAME}-delameter
DEPENDS_PATH = scripts/diagrams

VENV_PATH = venv

include .env.dist
-include .env
export
VERSION ?= 0.0.0

NOW    := $(shell LC_TIME=en_US.UTF-8 date '+%H:%M:%S %-e-%b-%y')
BOLD   := $(shell tput -Txterm bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
BLUE   := $(shell tput -Txterm setaf 4)
DIM    := $(shell tput -Txterm dim)
RESET  := $(shell printf '\e[m')
                                # tput -Txterm sgr0 returns SGR-0 with
                                # nF code switching esq, which displaces the columns
## Common commands

help:   ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^(##)\s?(\s*#?[^#]+)#*\s*(.*)/\1${YELLOW}\2${RESET}#\3/; s/(.+):(#|\s)+(.+)/##   ${GREEN}\1${RESET}#\3/; s/\*(\w+)\*/${BOLD}\1${RESET}/g; 2~1s/<([ )*<@>.A-Za-z0-9_(-]+)>/${DIM}\1${RESET}/gi' -e 's/(\x1b\[)33m#/\136m/' | column -ts# | sed -Ee 's/ {3}>/ >/'


all:   ## Prepare, run tests, generate docs and reports, build module
all: prepare prepare-pdf auto-all test doctest coverage docs-all build
# CI (on push into master): prepare prepare-pdf set-version set-tag auto-all test doctest coverage docs-all build upload upload-doc?

prepare:  ## Prepare environment for module building
	rm -vrf ${VENV_PATH}
	if [ ! -f .env ] ; then cp -u .env.dist .env && sed -i -Ee '/^VERSION=/d' .env.build ; fi
	python3 -m venv ${VENV_PATH}
	venv/bin/pip3 install --upgrade build twine
	venv/bin/pip3 install -r requirements-dev.txt

prepare-pdf:  ## Prepare environment for pdf rendering
	sudo apt install texlive-latex-recommended \
					 texlive-fonts-recommended \
					 texlive-latex-extra latexmk

freeze:  ## Actualize the requirements.txt file(s)  <venv>
	venv/bin/pip3 freeze -r requirements-dev.txt --all --exclude-editable > requirements-dev.txt.new
	mv requirements-dev.txt.new requirements-dev.txt

demolish-build:  ## Purge build output folders
	rm -f -v dist/* ${PROJECT_NAME_PUBLIC}.egg-info/* ${PROJECT_NAME_PRIVATE}.egg-info/*


## Automation

auto-all:  ## Run full cycle of automatic operations
auto-all: preprocess-rgb update-index

preprocess-rgb:  ## Transform interm. RGB config to suitable for embedding
	PYTHONPATH=. venv/bin/python scripts/preprocess_rgb.py
	PYTHONPATH=. venv/bin/python scripts/print_rgb.py

update-index:  ## Process color configs and update library color index sources
	echo NOP



## Testing / Pre-build

set-version: ## Set new package version
	@echo "Current version: ${YELLOW}${VERSION}${RESET}"
	read -p "New version (press enter to keep current): " VERSION
	if [ -z $$VERSION ] ; then echo "No changes" && return 0 ; fi
	sed -E -i "s/^VERSION.+/VERSION=$$VERSION/" .env.dist
	sed -E -i "s/^version.+/version = $$VERSION/" setup.cfg
	sed -E -i "s/^__version__.+/__version__ = '$$VERSION'/" ${PROJECT_NAME}/_version.py
	echo "Updated version: ${GREEN}$$VERSION${RESET}"

test: ## Run pytest
	venv/bin/python -m pytest tests

test-verbose: ## Run pytest with detailed output
	venv/bin/python -m pytest tests -v

test-debug: ## Run pytest with VERY detailed output
	venv/bin/python -m pytest tests -v --log-cli-level=DEBUG

doctest: ## Run doctest
	. venv/bin/activate
	sphinx-build docs docs/_build -b doctest -q && echo "Doctest ${GREEN}OK${RESET}"

coverage: ## Run coverage and make a report
	rm -v coverage-report/*
	. venv/bin/activate
	PYTHONPATH=`pwd` coverage run tests -vv
	coverage report
	coverage html
	if [ -n $$DISPLAY ] ; then xdg-open coverage-report/index.html ; fi

depends:  ## Build and display module dependency graph
	rm -vrf ${DEPENDS_PATH}
	mkdir -p ${DEPENDS_PATH}
	./pydeps.sh ${PROJECT_NAME} ${DEPENDS_PATH}

#update-readme: # Generate and rewrite README
#	. venv/bin/activate
#	PYTHONPATH=`pwd` python3 -s dev/readme/update_readme.py


## Documentation

reinit-docs: ## Erase and reinit docs with auto table of contents
	rm -v docs/*.rst
	. venv/bin/activate
	sphinx-apidoc --force --separate --module-first --tocfile index --output-dir docs ${PROJECT_NAME}

demolish-docs:  ## Purge docs output folder
	rm -rvf docs/_build

docs: ## (Re)build HTML documentation  <from scratch>
docs: demolish-docs docs-html

docs-html: ## Build HTML documentation  <caching allowed>
	mkdir -p docs-build
	venv/bin/sphinx-build docs docs/_build -b html -n
	#find docs/_build -type f -name '*.html' | sort | xargs -n1 grep -HnT ^ | sed s@^docs/_build/@@ > docs-build/${PROJECT_NAME}.html.dump
	#if [ -n "${DISPLAY}" ] ; then xdg-open docs/_build/index.html ; fi
	if command -v notify-send ; then notify-send -i ${PWD}/docs/_static_src/logo-white-bg.svg pytermor 'HTML docs updated ${NOW}' ; fi

docs-pdf: ## Build PDF documentation  <caching allowed>
	mkdir -p docs-build
	yes "" | venv/bin/sphinx-build -M latexpdf docs docs/_build -n  # twice for building pdf toc
	yes "" | venv/bin/sphinx-build -M latexpdf docs docs/_build     # @FIXME broken unicode
	mv docs/_build/latex/${PROJECT_NAME}.pdf docs-build/${PROJECT_NAME}.pdf
	if [ -n "${DISPLAY}" ] ; then xdg-open docs-build/${PROJECT_NAME}.pdf ; fi

docs-man: ## Build man pages  <caching allowed>
	sed -i.bak -Ee 's/^.+<<<MAKE_DOCS_MAN<<</#&/' docs/conf.py
	venv/bin/sphinx-build docs docs/_build -b man -n || echo 'Generation failed'
	mv docs/conf.py.bak docs/conf.py
	mv docs/_build/${PROJECT_NAME}.1 docs-build/${PROJECT_NAME}.1
	if command -v maf &>/dev/null; then maf docs-build/${PROJECT_NAME}.1; else man docs-build/${PROJECT_NAME}.1; fi

docs-all: ## (Re)build documentation in all formats
docs-all: demolish-docs docs docs-pdf docs-man
	@echo
	@$(call log_success,$$(du -h docs-build/*)) | sed -E '1s/^(..).{7}/\1SUMMARY/'


## Releasing (dev)

build-dev: ## Create new private build  <*-delameter>
build-dev: demolish-build
	sed -E -i "s/^name.+/name = ${PROJECT_NAME_PRIVATE}/" setup.cfg
	. venv/bin/activate
	python3 -m build --outdir dist-dev
	sed -E -i "s/^name.+/name = ${PROJECT_NAME_PUBLIC}/" setup.cfg

upload-dev: ## Upload latest private build to dev repo
	. venv/bin/activate
	python3 -m twine upload --repository testpypi dist-dev/* \
			-u ${PYPI_USERNAME} -p ${PYPI_PASSWORD_DEV} --verbose

install-dev: ## Install latest private build from dev repo
	. "${ES7S_VENV}/bin/activate"
	pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME_PRIVATE}==${VERSION}

install-dev-public: ## Install latest *public* build from dev repo
	. "${ES7S_VENV}/bin/activate"
	pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME_PUBLIC}==${VERSION}


## Releasing (MASTER)

build: ## Create new *public* build
build: demolish-build
	. venv/bin/activate
	python3 -m build

upload: ## Upload latest *public* build to MASTER repo
	. venv/bin/activate
	python3 -m twine upload dist/* -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} --verbose

install: ## Install latest *public* build from MASTER repo
	. "${ES7S_VENV}/bin/activate"
	pip install ${PROJECT_NAME_PUBLIC}==${VERSION}


