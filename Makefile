## pytermor             ## ANSI formatted terminal output toolset
## (c) 2022             ## A. Shavykin <0.delameter@gmail.com>
##----------------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test docs

PROJECT_NAME = pytermor
PROJECT_NAME_PUBLIC = ${PROJECT_NAME}
PROJECT_NAME_PRIVATE = ${PROJECT_NAME}-delameter
DEPENDS_PATH = scripts/diagrams
LOCALHOST_URL = http://localhost/pytermor
LOCALHOST_WRITE_PATH = localhost

VENV_PATH = venv
PYTHONPATH = .

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
all: reinit-venv prepare-pdf auto-all test doctest coverage docs-all build
# CI (on push into master): prepare prepare-pdf set-version set-tag auto-all test doctest coverage docs-all build upload upload-doc?

reinit-venv:  ## Prepare environment for module building
	rm -vrf ${VENV_PATH}
	if [ ! -f .env ] ; then cp -u .env.dist .env && sed -i -Ee '/^VERSION=/d' .env ; fi
	python3 -m venv ${VENV_PATH}
	${VENV_PATH}/bin/pip install --upgrade build twine
	${VENV_PATH}/bin/pip install -r requirements-dev.txt

prepare-pdf:  ## Prepare environment for pdf rendering
	sudo apt install texlive-latex-recommended \
					 texlive-fonts-recommended \
					 texlive-latex-extra \
					 latexmk

##
## Examples

ex-list-renderers:  ## Run "list renderers" example
	${VENV_PATH}/bin/python examples/list_renderers.py

ex-terminal-color-mode:  ## Run "terminal color mode" example
	${VENV_PATH}/bin/python examples/terminal_color_mode.py

ex-approximate:  ## Run "approximate color" example
	${VENV_PATH}/bin/python examples/approximate.py

##
## Automation

auto-all:  ## Run full cycle of automatic operations
auto-all: preprocess-rgb build-cval

preprocess-rgb:  ## Transform interm. RGB config to suitable for embedding
	${VENV_PATH}/bin/python dev/preprocess_rgb.py

build-cval: ## Process color configs and update library color values source file
	${VENV_PATH}/bin/python dev/build_cval.py

#update-readme: # Generate and rewrite README
#	. venv/bin/activate
#	PYTHONPATH=`pwd` python3 -s dev/readme/update_readme.py


##
## Testing / Pre-build

show-version: ## Show current package version
	@echo "Current version: ${YELLOW}${VERSION}${RESET}"

set-version: ## Set new package version
	@echo "Current version: ${YELLOW}${VERSION}${RESET}"
	read -p "New version (press enter to keep current): " VERSION
	if [ -z $$VERSION ] ; then echo "No changes" && return 0 ; fi
	sed -E -i "s/^VERSION.+/VERSION=$$VERSION/" .env.dist
	sed -E -i "s/^version.+/version = $$VERSION/" setup.cfg
	sed -E -i "s/^__version__.+/__version__ = '$$VERSION'/" ${PROJECT_NAME}/_version.py
	echo "Updated version: ${GREEN}$$VERSION${RESET}"

test: ## Run pytest
	${VENV_PATH}/bin/python -m pytest tests

test-verbose: ## Run pytest with detailed output
	${VENV_PATH}/bin/python -m pytest tests -v

test-debug: ## Run pytest with VERY detailed output
	${VENV_PATH}/bin/python -m pytest tests -v --log-cli-level=DEBUG

doctest: ## Run doctest
	@${VENV_PATH}/bin/sphinx-build docs docs/_build -b doctest -Eq && echo "Doctest ${GREEN}OK${RESET}"

coverage: ## Run coverage and make a report
	rm -v coverage-report/*
	${VENV_PATH}/bin/coverage run tests -vv
	${VENV_PATH}/bin/coverage report
	${VENV_PATH}/bin/coverage html
	if [ -d ${LOCALHOST_WRITE_PATH} ] ; then \
    	mkdir -p ${LOCALHOST_WRITE_PATH}/coverage-report && \
	    cp -auv coverage-report/* ${LOCALHOST_WRITE_PATH}/coverage-report/
	fi

open-coverage:  ## Open coverage report in browser
	if [ -z "${DISPLAY}" ] ; then echo 'ERROR: No $$DISPLAY' && return 1 ; fi
	if [ -d localhost ] ; then xdg-open ${LOCALHOST_URL}/coverage-report ; else xdg-open coverage-report/index.html ; fi

depends:  ## Build and display module dependency graph
	rm -vrf ${DEPENDS_PATH}
	mkdir -p ${DEPENDS_PATH}
	./pydeps.sh ${PROJECT_NAME} ${DEPENDS_PATH}

##
## Documentation

reinit-docs: ## Erase and reinit docs with auto table of contents
	rm -v docs/*.rst
	${VENV_PATH}/bin/sphinx-apidoc --force --separate --module-first --tocfile index --output-dir docs ${PROJECT_NAME}

demolish-docs:  ## Purge docs output folder
	rm -rvf docs/_build

open-docs-html:  ## Open HTML docs in browser
	if [ -z "${DISPLAY}" ] ; then echo 'ERROR: No $$DISPLAY' && return 1 ; fi
	if [ -d localhost ] ; then xdg-open ${LOCALHOST_URL}/docs ; else xdg-open docs/_build/index.html ; fi

docs: ## (Re)build HTML documentation  <no cache>
docs: demolish-docs docs-html

docs-html: ## Build HTML documentation  <caching allowed>
	mkdir -p docs-build
	if ! ${VENV_PATH}/bin/sphinx-build docs docs/_build -b html -n ; then \
    	notify-send -i important pytermor 'HTML docs build failed ${NOW}' && \
    	return 1 ; \
    fi
	if [ -d localhost ] ; then \
    	mkdir -p ${LOCALHOST_WRITE_PATH}/docs && \
		cp -auv docs/_build/* ${LOCALHOST_WRITE_PATH}/docs/ ; \
    fi
	#find docs/_build -type f -name '*.html' | sort | xargs -n1 grep -HnT ^ | sed s@^docs/_build/@@ > docs-build/${PROJECT_NAME}.html.dump
	if command -v notify-send ; then notify-send -i ${PWD}/docs/_static_src/logo-white-bg.svg 'pytermor ${VERSION}' 'HTML docs updated ${NOW}' ; fi

docs-pdf: ## Build PDF documentation  <caching allowed>
	mkdir -p docs-build
	yes "" | ${VENV_PATH}/bin/sphinx-build -M latexpdf docs docs/_build -n >/dev/null # twice for building pdf toc
	yes "" | ${VENV_PATH}/bin/sphinx-build -M latexpdf docs docs/_build    >/dev/null # @FIXME broken unicode
	mv docs/_build/latex/${PROJECT_NAME}.pdf docs-build/${PROJECT_NAME}.pdf
	if [ -n "${DISPLAY}" ] ; then xdg-open docs-build/${PROJECT_NAME}.pdf ; fi

docs-man: ## Build man pages  <caching allowed>
	sed -i.bak -Ee 's/^.+<<<MAKE_DOCS_MAN<<</#&/' docs/conf.py
	${VENV_PATH}/bin/sphinx-build docs docs/_build -b man -n || echo 'Generation failed'
	mv docs/conf.py.bak docs/conf.py
	mv docs/_build/${PROJECT_NAME}.1 docs-build/${PROJECT_NAME}.1
	if command -v maf &>/dev/null; then maf docs-build/${PROJECT_NAME}.1; else man docs-build/${PROJECT_NAME}.1; fi

docs-all: ## (Re)build documentation in all formats  <no cache>
docs-all: demolish-docs docs docs-pdf docs-man
	@echo
	@$(call log_success,$$(du -h docs-build/*)) | sed -E '1s/^(..).{7}/\1SUMMARY/'

##
## Building / Packaging

freeze:  ## Actualize the requirements.txt file(s)  <venv>
	${VENV_PATH}/bin/pip freeze -r requirements-dev.txt --all --exclude-editable > requirements-dev.txt.tmp
	sed -i -Ee '/were added by pip/ s/.+//' requirements-dev.txt.tmp
	mv requirements-dev.txt.tmp requirements-dev.txt

demolish-build:  ## Purge build output folders
	rm -f -v dist/* ${PROJECT_NAME_PUBLIC}.egg-info/* ${PROJECT_NAME_PRIVATE}.egg-info/*

### dev

build-dev: ## Create new private build  <*-delameter>
build-dev: demolish-build
	sed -E -i "s/^name.+/name = ${PROJECT_NAME_PRIVATE}/" setup.cfg
	${VENV_PATH}/bin/python3 -m build --outdir dist-dev
	sed -E -i "s/^name.+/name = ${PROJECT_NAME_PUBLIC}/" setup.cfg

upload-dev: ## Upload latest private build to dev repo
	${VENV_PATH}/bin/twine upload --repository testpypi dist-dev/* \
			-u ${PYPI_USERNAME} -p ${PYPI_PASSWORD_DEV} --verbose

install-dev: ## Install latest private build from dev repo
	${VENV_PATH}/bin/pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME_PRIVATE}==${VERSION}

install-dev-public: ## Install latest *public* build from dev repo
	${VENV_PATH}/bin/pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME_PUBLIC}==${VERSION}

### release

build: ## Create new *public* build
build: demolish-build
	${VENV_PATH}/bin/python -m build

upload: ## Upload latest *public* build to MASTER repo
	${VENV_PATH}/bin/twine upload dist/* -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} --verbose

install: ## Install latest *public* build from MASTER repo
	${VENV_PATH}/bin/pip install ${PROJECT_NAME_PUBLIC}==${VERSION}

##
