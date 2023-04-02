## pytermor             ## ANSI formatted terminal output toolset
## (c) 2022-2023        ## A. Shavykin <<0.delameter@gmail.com>>
##----------------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test docs

PROJECT_NAME = pytermor
HOST_DEFAULT_PYTHON = /usr/bin/python3

VENV_LOCAL_PATH = venv
DOCS_IN_PATH = docs
DOCS_OUT_PATH = docs-build
DEPENDS_PATH = misc/depends

LOCALHOST_URL = http://localhost/pt
LOCALHOST_WRITE_PATH = localhost

-include .env
export
VERSION := $(shell ./.version)

DOCKER_IMAGE = ghcr.io/delameter/pytermor
DOCKER_TAG = ${DOCKER_IMAGE}:${VERSION}
DOCKER_CONTAINER = pytermor-build-${VERSION}

NOW    := $(shell LC_TIME=en_US.UTF-8 date '+%H:%M:%S %-e-%b-%y')
BOLD   := $(shell tput -Txterm bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
BLUE   := $(shell tput -Txterm setaf 4)
DIM    := $(shell tput -Txterm dim)
RESET  := $(shell printf '\e[m')
                                # tput -Txterm sgr0 returns SGR-0 with
                                # nF code switching esq, which displaces the columns
## Common

help:   ## [any] Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^(##)\s?(\s*#?[^#]+)#*\s*(.*)/\1${YELLOW}\2${RESET}#\3/; s/(.+):(#|\s)+(.+)/##   ${GREEN}\1${RESET}#\3/; s/\*(\w+)\*/${BOLD}\1${RESET}/g; 2~1s/<([ )*<@>.A-Za-z0-9_(-]+)>/${DIM}\1${RESET}/gi' -e 's/(\x1b\[)33m#/\136m/' | column -ts# | sed -Ee 's/ {3}>/ >/'

init-venv:  ## [host] Prepare manual environment  <venv>
	${HOST_DEFAULT_PYTHON} -m venv --clear ${VENV_LOCAL_PATH}
	${VENV_LOCAL_PATH}/bin/python -m pip install -r requirements-build.txt
	${VENV_LOCAL_PATH}/bin/python -m pip install -r requirements-test.txt
	${VENV_LOCAL_PATH}/bin/python -m pytermor

init-hatch:  ## [host] Install build backend <system>
	pipx install hatch

init-system-pdf:  ## [host] Prepare environment for pdf rendering
	sudo apt install texlive-latex-recommended \
					 texlive-fonts-recommended \
					 texlive-latex-extra \
					 latexmk

cli: ## [host] Launch python interpreter  <hatch>
	hatch run python -uq

docker-cli: ## [host] Launch shell in a container
docker-cli: build-image
	docker run -it ${DOCKER_TAG} /bin/bash

all: ## [host] Run tests, generate docs and reports, build module
all: test cover update-coveralls docs-all build
# CI (on push into master): set-version set-tag auto-all test cover docs-all build upload upload-doc?

build-image-base: ## [host] Build base docker image
	docker build . --target python-texlive --tag delameter/python-texlive:3.8-2020

build-image: ## [host] Build docker image
	docker build . --tag ${DOCKER_TAG} \
    		--build-arg PYTERMOR_VERSION="${VERSION}" \
    		--build-arg IMAGE_BUILD_DATE="${NOW}"

_docker_run = (docker run -it --env-file .env --name ${DOCKER_CONTAINER} ${DOCKER_TAG} "$1")
_docker_run_rm = (docker run --rm -it --env-file .env --name ${DOCKER_CONTAINER} ${DOCKER_TAG} "$1")
_docker_cp_docs = (docker cp ${DOCKER_CONTAINER}:/opt/${DOCS_OUT_PATH} ${PWD})
_docker_cp_dist = (docker cp ${DOCKER_CONTAINER}:/opt/dist ${PWD})
_docker_rm = (docker rm ${DOCKER_CONTAINER})

docker-all:  ## [host] Run tests, build module and update docs in docker container
docker-all: demolish-docs build-image
	$(call _docker_run,"make all")
	$(call _docker_cp_docs)
	$(call _docker_cp_dist)
	$(call _docker_rm)

docker-cover:  ## [host] Measure coverage in docker container
docker-cover: build-image
	$(call _docker_run_rm,"make cover update-coveralls")

docker-docs-pdf:  ## [host] Update PDF docs in docker container
docker-docs-pdf: build-image
	$(call _docker_run,"make docs-pdf")
	$(call _docker_cp_docs)

##
## Automation

pre-build:  ## Run full cycle of automatic operations (done on docker image building)
	export PT_ENV=build
	./.invoke python scripts/preprocess_rgb.py
	./.invoke python scripts/build_cval.py


##
## Versioning

show-version: ## Show current package version
	@hatch version | sed -Ee "s/.+/Current: ${CYAN}&${RESET}/"

_set_next_version = (hatch version $1 | sed -Ee "s/^(Old:)(.+)/\1${CYAN}\2${RESET}/; s/^(New:)(.+)/\1${YELLOW}\2${RESET}/")

set-next-version-dev: ## Increase version by <dev>
	@$(call _set_next_version,dev)

set-next-version-micro: ## Increase version by 0.0.1
	@$(call _set_next_version,micro | head -1)
	@$(call _set_next_version,dev | tail -1)

set-next-version-minor: ## Increase version by 0.1
	@$(call _set_next_version,minor | head -1)
	@$(call _set_next_version,dev | tail -1)

set-next-version-major: ## Increase version by 1
	@$(call _set_next_version,major | head -1)
	@$(call _set_next_version,dev | tail -1)

update-changelist:  ## Auto-update with new commits  <@CHANGES.rst>
	./update-changelist.sh


##
## Testing

test: ## Run pytest
	@PT_ENV=test ./.invoke pytest --quiet --tb=no

test-verbose: ## Run pytest with detailed output
	@PT_ENV=test ./.invoke pytest -v --failed-first

test-trace: ## Run pytest with detailed output  <@last_test_trace.log>
	@PT_ENV=test PYTERMOR_TRACE_RENDERS=1 \
      ./.invoke pytest -v --failed-first --log-file-level=1 --log-file=last_test_trace.log


##
## Coverage / dependencies

cover: ## Run coverage and make a report
	export PT_ENV=test
	rm -v coverage-report/*
	./.invoke coverage run -m pytest
	./.invoke coverage html
	./.invoke coverage json
	./.invoke coverage report

	if [ -d "${LOCALHOST_WRITE_PATH}" ] ; then \
    	mkdir -p ${LOCALHOST_WRITE_PATH}/coverage-report && \
	    cp -au coverage-report/* ${LOCALHOST_WRITE_PATH}/coverage-report/
	fi

open-coverage:  ## Open coverage report in browser
	if [ -z "${DISPLAY}" ] ; then echo 'ERROR: No $$DISPLAY' && return 1 ; fi
	if [ -d localhost ] ; then xdg-open ${LOCALHOST_URL}/coverage-report ; else xdg-open coverage-report/index.html ; fi

update-coveralls:  ## Manually send last coverage statistics  <coveralls.io>
	if [ -n "${SKIP_COVERALLS_UPDATE}" ] ; then echo "DISABLED" && return 0 ; fi
	@PT_ENV=test ./.invoke coveralls


depends:  ## Build module dependency graphs
	rm -vrf ${DEPENDS_PATH}
	mkdir -p ${DEPENDS_PATH}
	./pydeps.sh ${PROJECT_NAME} ${DEPENDS_PATH}

open-depends:  ## Open dependency graph output directory
	xdg-open ./${DEPENDS_PATH}

##
## Documentation

reinit-docs: ## Purge and recreate docs with auto table of contents
	export PT_ENV=build
	rm -rfv ${DOCS_IN_PATH}/*
	./.invoke sphinx-apidoc --force --separate --module-first --tocfile index --output-dir ${DOCS_IN_PATH} ${PROJECT_NAME}

demolish-docs:  ## Purge docs temp output folder
	-rm -rvf ${DOCS_IN_PATH}/_build/* ${DOCS_IN_PATH}/_build/.*

docs: ## (Re)build HTML documentation  <no cache>
docs: depends demolish-docs docs-html

docs-html: ## Build HTML documentation  <caching allowed>
	export PT_ENV=build
	mkdir -p docs-build
	if ! ./.invoke sphinx-build ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -b html -n ; then \
    	notify-send -i important pytermor 'HTML docs build failed ${NOW}' && \
    	return 1 ; \
    fi
	cp -auv ${DOCS_IN_PATH}/_build/* ${DOCS_OUT_PATH}/${VERSION}/ ; \
	if [ -d localhost ] ; then \
    	mkdir -p ${LOCALHOST_WRITE_PATH}/docs && \
		cp -auv ${DOCS_IN_PATH}/_build/* ${LOCALHOST_WRITE_PATH}/docs/ ; \
    fi
	#find docs/_build -type f -name '*.html' | sort | xargs -n1 grep -HnT ^ | sed s@^docs/_build/@@ > docs-build/${PROJECT_NAME}.html.dump
	#if command -v notify-send ; then notify-send -i ${PWD}/${DOCS_IN_PATH}/_static_src/logo-white-bg.svg 'pytermor ${VERSION}' 'HTML docs updated ${NOW}' ; fi

docs-pdf: ## Build PDF documentation  <caching allowed>
	export PT_ENV=build
	mkdir -p docs-build
	yes "" | ./.invoke sphinx-build -M latexpdf ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -n  # twice for building pdf toc
	yes "" | ./.invoke sphinx-build -M latexpdf ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build     # @FIXME broken unicode
	cp ${DOCS_IN_PATH}/_build/latex/${PROJECT_NAME}.pdf ${DOCS_OUT_PATH}/${VERSION}.pdf

docs-man: ## Build man pages  <caching allowed>
	export PT_ENV=build
	mkdir -p docs-build
	sed -i.bak -Ee 's/^.+<<<MAKE_DOCS_MAN<<</#&/' ${DOCS_IN_PATH}/conf.py
	./.invoke sphinx-build ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -b man -n || echo 'Generation failed'
	mv ${DOCS_IN_PATH}/conf.py.bak ${DOCS_IN_PATH}/conf.py
	cp ${DOCS_IN_PATH}/_build/${PROJECT_NAME}.1 ${DOCS_OUT_PATH}/${VERSION}.1
	if [ -z "${DISPLAY}" ] ; then return 0 ; fi
	COLUMNS=120 man ${DOCS_OUT_PATH}/${PROJECT_NAME}.1 2>/dev/null | sed -Ee '/корректность/d' | lpr -p  # @TODO ебаный стыд

docs-all: ## (Re)build documentation in all formats  <no cache>
docs-all: depends demolish-docs docs docs-pdf docs-man

open-docs-html:  ## Open HTML docs in browser
	if [ -z "${DISPLAY}" ] ; then echo 'ERROR: No $$DISPLAY' && return 1 ; fi
	if [ -d localhost ] ; then xdg-open ${LOCALHOST_URL}/docs ; else xdg-open ${DOCS_IN_PATH}/_build/index.html ; fi

open-docs-pdf:  ## Open PDF docs in reader
	if [ -z "${DISPLAY}" ] ; then echo 'ERROR: No $$DISPLAY' && return 1 ; fi
	xdg-open ${DOCS_OUT_PATH}/${VERSION}.pdf

##
## Building / Packaging
### *

_freeze = (hatch -e $1 run pip freeze -q --exclude-editable | sed --unbuffered -Ee '/^Checking/d' | tee /dev/stderr > requirements-$1.txt)

freeze:  ## Update requirements-*.txt   <hatch>
	$(call _freeze,test)
	$(call _freeze,build)

demolish-build:  ## Delete build output folders  <hatch>
	hatch clean

build: ## Build a package   <hatch>
build: demolish-build
	hatch -e build build

### test

publish-test: ## Upload latest build to test repo   <hatch>
	hatch -e build publish -r test -u "${PYPI_USERNAME}" -a "${PYPI_PASSWORD_TEST}"

install-test: ## Install latest build from test repo  <system>
	python -m pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME}==${VERSION}


### release

publish: ## Upload last build (=> PRIMARY registry)   <hatch>
	if [ -n "${SKIP_MODULE_UPLOAD}" ] ; then return 0 ; fi
	hatch -e build publish -u "${PYPI_USERNAME}" -a "${PYPI_PASSWORD}"

install: ## Install latest build from PRIMARY repo  <system>
	python -m pip install ${PROJECT_NAME}==${VERSION}

##
