## pytermor             ## ANSI formatted terminal output toolset
## (c) 2022-2023        ## A. Shavykin <<0.delameter@gmail.com>>
##----------------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test docs

PROJECT_NAME = pytermor
HOST_DEFAULT_PYTHON = /usr/bin/python3.10

VENV_LOCAL_PATH = venv
DOCS_IN_PATH = docs
DOCS_OUT_PATH = docs-build
DEPENDS_PATH = misc/depends
VERSION_FILE_PATH = pytermor/_version.py

LOCALHOST_URL = http://localhost/pt
LOCALHOST_WRITE_PATH = localhost

-include .env
export
VERSION := $(shell ./.version)

$(shell touch .mkrunid)
RUN_ID != bash -c 'tee <<< $$(( $$(head -1 .mkrunid)+1 )) .mkrunid'

DOCKER_IMAGE = ghcr.io/delameter/pytermor
DOCKER_TAG = ${DOCKER_IMAGE}:${VERSION}
DOCKER_CONTAINER = pytermor-build-${VERSION}

DOCKER_BASE_IMAGE = delameter/python-texlive
DOCKER_BASE_TAG = ${DOCKER_BASE_IMAGE}:3.10-2022

NOW    := $(shell LC_TIME=en_US.UTF-8 date --rfc-3339=seconds)
BOLD   := $(shell tput -Txterm bold)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
BLUE   := $(shell tput -Txterm setaf 4)
CYAN   := $(shell tput -Txterm setaf 6)
GRAY   := $(shell tput -Txterm setaf 7)
DIM    := $(shell tput -Txterm dim)
RESET  := $(shell printf '\e[m')
                                # tput -Txterm sgr0 returns SGR-0 with
                                # nF code switching esq, which displaces the columns
## Common

help:   ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^(##)\s?(\s*#?[^#]+)#*\s*(.*)/\1${YELLOW}\2${RESET}#\3/; s/(.+):(#|\s)+(.+)/##   ${GREEN}\1${RESET}#\3/; s/\*(\w+)\*/${BOLD}\1${RESET}/g; 2~1s/<([ )*<@>.A-Za-z0-9_(-]+)>/${DIM}\1${RESET}/gi' -e 's/(\x1b\[)33m#/\136m/' | column -ts# | sed -Ee 's/ {3}>/ >/'
	PYTERMOR_FORCE_OUTPUT_MODE=xterm_256 ${VENV_LOCAL_PATH}/bin/python .run-startup.py | tail -2 ; echo

cli: ## Launch python interpreter  <hatch>
	hatch run python -uq

all: ## Run tests, generate docs and reports, build module
all: test-verbose cover update-coveralls docs-all build
	# CI (on push into master): set-version set-tag auto-all test cover docs-all build upload upload-doc?

.:
## Initialization

init-venv:  ## Prepare manual environment  <venv>
	${HOST_DEFAULT_PYTHON} -m venv --clear ${VENV_LOCAL_PATH}
	${VENV_LOCAL_PATH}/bin/python -m pip install -r requirements-build.txt -r requirements-test.txt
	${VENV_LOCAL_PATH}/bin/python -m pytermor

init-hatch:  ## Install build backend <system>
	pipx install hatch

init-system-pdf:  ## Prepare environment for pdf rendering
	sudo apt install texlive-latex-recommended \
					 texlive-fonts-recommended \
					 texlive-latex-extra \
					 latexmk \
					 dvipng \
					 dvisvgm

.:
## Docker

docker-cli: ## [host] Launch shell in a container
docker-cli: build-image
	docker run -it ${DOCKER_TAG} /bin/bash

build-image-base: ## [host] Build base docker image
	docker build . \
    	--target python-texlive \
    	--tag ${DOCKER_BASE_TAG}

build-image: ## [host] Build docker image
	docker build . \
    	--build-arg PYTERMOR_VERSION="${VERSION}" \
    	--build-arg IMAGE_BUILD_DATE="${NOW}" \
    	--tag ${DOCKER_TAG}

_docker_run = (docker run -it --env-file .env --name ${DOCKER_CONTAINER} ${DOCKER_TAG} "$1")
_docker_run_rm = (docker run --rm -it --env-file .env --name ${DOCKER_CONTAINER} ${DOCKER_TAG} "$1")
_docker_cp_docs = (docker cp ${DOCKER_CONTAINER}:/opt/${DOCS_OUT_PATH} ${PWD})
_docker_cp_dist = (docker cp ${DOCKER_CONTAINER}:/opt/dist ${PWD})
_docker_rm = (docker rm ${DOCKER_CONTAINER} 2>/dev/null >&2 ; return 0)

docker-all:  ## Run tests, build module and update docs in docker container
docker-all: demolish-docs build-image make-docs-out-dir
	$(call _docker_rm)
	$(call _docker_run,"make all")
	$(call _docker_cp_docs)
	$(call _docker_cp_dist)
	$(call _docker_rm)

docker-cover:  ## Measure coverage in docker container
docker-cover: build-image
	$(call _docker_run_rm,"make cover update-coveralls")

docker-docs-html:  ## Update PDF docs in docker container
docker-docs-html: build-image make-docs-out-dir
	$(call _docker_run,"make docs-html")
	$(call _docker_cp_docs)

docker-docs-pdf:  ## Update PDF docs in docker container
docker-docs-pdf: build-image make-docs-out-dir
	$(call _docker_run,"make docs-pdf")
	$(call _docker_cp_docs)

make-docs-out-dir:
	@mkdir -p ${DOCS_OUT_PATH}/${VERSION}

_ensure_x11 = ([ -n "${DISPLAY}" ] && return; echo 'ERROR: No $$DISPLAY'; return 1)

.:
## Automation

pre-build:  ## Update CVAL  <runs on docker image building>
	@export PT_ENV=build
	./.invoke python scripts/preprocess_rgb.py && \
      ./.invoke python scripts/build_cval.py

lint:  ## Run flake8
	@export PT_ENV=test
	./.invoke flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	./.invoke flake8 . --count --exit-zero --max-line-length=127 --statistics

.:
## Testing

test: ## Run pytest
	@PT_ENV=test ./.invoke pytest \
		--quiet \
		--tb=line

test-verbose: ## Run pytest with detailed output
	@PT_ENV=test ./.invoke pytest -v \
		--maxfail 1 \
		--log-level=10

test-trace: ## Run pytest with detailed output  <@last_test_trace.log>
	@PT_ENV=test ./.invoke pytest -v \
		--maxfail 1 \
		--log-file-level=1 \
		--log-file=last_test_trace.log
	# optional: PYTERMOR_TRACE_RENDERS=1
	@/usr/bin/ls --size --si last_test_trace.log

.:
## Profiling

profile-import-tuna:  ## Profile imports
	@PT_ENV=test \
		./.invoke python -X importtime -m pytermor 2> ./import.log && \
		tuna ./import.log

.:
## Coverage / dependencies

cover: ## Run coverage and make a report
	@export PT_ENV=test
	@rm -v coverage-report/*
	./.invoke coverage run -m pytest -- --maxfail 100
	./.invoke coverage html
	./.invoke coverage json
	./.invoke coverage report
	@$(call _notify,success,Coverage $$(jq -r < coverage.json .totals.percent_covered_display)%)
	@if [ -d "${LOCALHOST_WRITE_PATH}" ] ; then \
	    mkdir -p ${LOCALHOST_WRITE_PATH}/coverage-report && \
	    cp -au coverage-report/* ${LOCALHOST_WRITE_PATH}/coverage-report/
	fi

open-coverage:  ## Open coverage report in browser
	@$(call _ensure_x11) || return
	@[ -d localhost ] && xdg-open ${LOCALHOST_URL}/coverage-report || xdg-open coverage-report/index.html

update-coveralls:  ## Manually send last coverage statistics  <coveralls.io>
	@if [ -n "${SKIP_COVERALLS_UPDATE}" ] ; then echo "DISABLED" && return 0 ; fi
	@PT_ENV=test ./.invoke coveralls

depends:  ## Build module dependency graphs
	@rm -vrf ${DEPENDS_PATH}
	@mkdir -p ${DEPENDS_PATH}
	@./pydeps.sh ${PROJECT_NAME} ${DEPENDS_PATH}

open-depends:  ## Open dependency graph output directory
	@$(call _ensure_x11) || return
	@xdg-open ./${DEPENDS_PATH}

.:
## Documentation

reinit-docs: ## Purge and recreate docs with auto table of contents
	@export PT_ENV=build
	@rm -rfv ${DOCS_IN_PATH}/*
	./.invoke sphinx-apidoc --force --separate --module-first --tocfile index --output-dir ${DOCS_IN_PATH} ${PROJECT_NAME}

demolish-docs:  ## Purge docs temp output folder
	-rm -rvf ${DOCS_IN_PATH}/_build/* ${DOCS_IN_PATH}/_build/.* ${DOCS_IN_PATH}/_cache/*

docs: ## (Re)build HTML documentation  <no cache>
docs: depends demolish-docs docs-html

_build_html = (./.invoke sphinx-build ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -b html -d ${DOCS_IN_PATH}/_cache -n)
_build_pdf = (yes "" | ./.invoke sphinx-build -M latexpdf ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -d ${DOCS_IN_PATH}/_cache $1)
_build_man = (./.invoke sphinx-build ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -b man -d ${DOCS_IN_PATH}/_cache -n )
_notify = (command -v es7s >/dev/null && es7s exec notify -s $1 "${PROJECT_NAME} ${VERSION}" "[\#${RUN_ID}] ${2}")

docs-html: ## Build HTML documentation  <caching allowed>
	@export PT_ENV=build
	@mkdir -p ${DOCS_OUT_PATH}/${VERSION}
	$(call _build_html) || { $(call _notify,error,HTML docs build failed) ; return 1 ; }
	@cp -auv ${DOCS_IN_PATH}/_build/* ${DOCS_OUT_PATH}/${VERSION}/ ; \
	if [ -d localhost ] ; then \
    	mkdir -p ${LOCALHOST_WRITE_PATH}/docs && \
		cp -auv ${DOCS_IN_PATH}/_build/* ${LOCALHOST_WRITE_PATH}/docs/ ; \
    fi
	@$(call _notify,success,HTML docs updated) || return 0
	#find docs/_build -type f -name '*.html' | sort | xargs -n1 grep -HnT ^ | sed s@^docs/_build/@@ > docs-build/${PROJECT_NAME}.html.dump

docs-pdf: ## Build PDF documentation  <caching allowed>
	@export PT_ENV=build
	@mkdir -p docs-build
	[ ! -f ${DOCS_IN_PATH}/_build/latex/${PROJECT_NAME}.toc ] && $(call _build_pdf,-n) 	# @FIXME broken unicode
	$(call _build_pdf)  # 2nd time for TOC and INDEX building
	$(call _build_pdf)  # 3rd time for TOC rebuilding (to include INDEX, mama-mia)
	@cp -v ${DOCS_IN_PATH}/_build/latex/${PROJECT_NAME}.pdf ${DOCS_OUT_PATH}/${VERSION}.pdf
	@$(call _notify,success,PDF docs updated) || return 0

docs-man: ## Build man pages  <caching allowed>
	@export PT_ENV=build
	@mkdir -p docs-build
	@sed -i.bak -Ee 's/^.+<<<MAKE_DOCS_MAN<<</#&/' ${DOCS_IN_PATH}/conf.py
	$(call _build_man) || { $(call _notify,error,MAN docs build failed) ; return 1 ; }
	@mv ${DOCS_IN_PATH}/conf.py.bak ${DOCS_IN_PATH}/conf.py
	@cp ${DOCS_IN_PATH}/_build/${PROJECT_NAME}.1 ${DOCS_OUT_PATH}/${VERSION}.1
	@$(call _notify,success,MAN docs updated) || return 0

print-man:
	COLUMNS=120 man ${DOCS_OUT_PATH}/${PROJECT_NAME}.1 2>/dev/null | sed -Ee '/корректность/d' | lpr -p  # @TODO ебаный стыд

docs-all: ## (Re)build documentation in all formats  <no cache>
docs-all: depends demolish-docs docs docs-pdf docs-man

open-docs-html:  ## Open HTML docs in browser
	@$(call _ensure_x11) || return
	@[ -d localhost ] && xdg-open ${LOCALHOST_URL}/docs || xdg-open ${DOCS_IN_PATH}/_build/index.html

open-docs-pdf:  ## Open PDF docs in reader
	@$(call _ensure_x11) || return
	@xdg-open ${DOCS_OUT_PATH}/${VERSION}.pdf

.:
## Packaging

show-version: ## Show current package version
	@hatch version | sed -Ee "s/.+/Current: ${CYAN}&${RESET}/"

tag-version: ## Tag current git branch HEAD with the current version
	@git tag $(shell hatch version | cut -f1,2  -d\.) && git log -1

_set_next_version = (hatch version $1 | \
						tr -d '\n' | \
						sed -zEe "s/(Old:\s*)(\S+)(New:\s*)(\S+)/Version updated:\n\
										${CYAN} \2${RESET} -> ${YELLOW}\4${RESET}/" \
)
_set_current_date = (sed ${VERSION_FILE_PATH} -i -Ee 's/^(__updated__).+/\1 = "${NOW}"/w/dev/stdout' | cut -f2 -d'"')

#next-version-dev: ## Increase version by <dev>
#	@$(call _set_current_date)
#	@$(call _set_next_version,dev)
#	@echo

next-version-micro: ## Increase version by 0.0.1
	@$(call _set_current_date)
	@$(call _set_next_version,micro | head -2)
#	@$(call _set_next_version,dev | tail -1)
	@echo

next-version-minor: ## Increase version by 0.1
	@$(call _set_current_date)
	@$(call _set_next_version,minor | head -1)
#	@$(call _set_next_version,dev | tail -1)
	@echo

next-version-major: ## Increase version by 1
	@$(call _set_current_date)
	@$(call _set_next_version,major | head -1)
#	@$(call _set_next_version,dev | tail -1)
	@echo

set-current-date:  # Update timestamp in version file (done automatically)
	@$(call _set_current_date)

update-changelist:  ## Auto-update with new commits  <@CHANGES.rst>
	@./update-changelist.sh

.:
## Building / Publishing

_freeze = (	echo "${BSEP}\e[34mFreezing \e[1;94m$1\e[22;34m:\e[m\n${BSEP}"; \
			hatch -e $1 run pip freeze -q --exclude-editable | \
				sed --unbuffered -E -e '/^(Checking|Syncing|Creating|Installing)/d' | \
				fgrep -e pytermor -v | \
				tee requirements-$1.txt | \
				sed --unbuffered -E -e 's/^([a-zA-Z0-9_-]+)/\x1b[32m\1\x1b[m/' \
									-e 's/([0-9.]+|@[a-zA-Z0-9_-]+)$$/\x1b[33m\1\x1b[m/'; \
			echo)

freeze:  ## Update requirements-*.txt   <hatch>
	@$(call _freeze,test)
	@$(call _freeze,build)
	@$(call _freeze,demo)

demolish-build:  ## Delete build output folders  <hatch>
	hatch clean

build: ## Build a package   <hatch>
build: demolish-build
	hatch -e build build

### dev

publish-dev: ## Upload latest build to dev registry   <hatch>
	hatch -e build publish -r "${PYPI_REPO_URL_DEV}" -u "${PYPI_USERNAME_DEV}" -a "${PYPI_PASSWORD_DEV}"

install-dev: ## Install latest build from dev registry  <system>
	python -m pip install -i "${PYPI_REPO_URL_DEV}/simple" ${PROJECT_NAME}==${VERSION}

### test

publish-test: ## Upload latest build to test registry   <hatch>
	hatch -e build publish -r test -u "${PYPI_USERNAME}" -a "${PYPI_PASSWORD_TEST}"

install-test: ## Install latest build from test registry  <system>
	python -m pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME}==${VERSION}


### release

publish: ## Upload last build (=> PRIMARY registry)   <hatch>
	@[ -n "${SKIP_MODULE_UPLOAD}" ] && return 0
	hatch -e build publish -u "${PYPI_USERNAME}" -a "${PYPI_PASSWORD}"

install: ## Install latest build from PRIMARY registry  <system>
	python -m pip install ${PROJECT_NAME}==${VERSION}

##
