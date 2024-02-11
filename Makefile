## pytermor             ## ANSI formatted terminal output toolset
## (c) 2022-2023        ## A. Shavykin <<0.delameter@gmail.com>>
##----------------------##-------------------------------------------------------------
.ONESHELL:
.PHONY: help test docs

PROJECT_NAME = pytermor

include .env.dist
-include .env
export
VERSION := $(shell ./.version)

$(shell touch .mkrunid)
RUN_ID != bash -c 'tee <<< $$(( $$(head -1 .mkrunid)+1 )) .mkrunid'

DOCKER_IMAGE = ghcr.io/delameter/pytermor
DOCKER_TAG = ${DOCKER_IMAGE}:${VERSION}
DOCKER_CONTAINER = pytermor-build-${VERSION}

NL      := $(shell printf '\n')
__      := $(shell printf '\e[m')
                                  # "tput -Txterm sgr0" also prints nF code
                                  # switching esq, which breaks the columns
NOW     := $(shell LC_TIME=en_US.UTF-8 date --rfc-3339=seconds)
NOW_H   := $(shell LC_TIME=en_US.UTF-8 date +%0e\ %b\ %H:%M)
BOLD    := $(shell tput -Txterm bold)
INV     := $(shell tput -Txterm smso)
NOINV   := $(shell tput -Txterm rmso)
NOBG    := $(shell tput -Txterm setab 0)
RED     := $(shell tput -Txterm setaf 1)
BGRED   := $(shell tput -Txterm setab 1)
GREEN   := $(shell tput -Txterm setaf 2)
HIGREEN := $(shell tput -Txterm setaf 10)
BGGREEN := $(shell tput -Txterm setab 2)
YELLOW  := $(shell tput -Txterm setaf 3)
BLUE    := $(shell tput -Txterm setaf 4)
CYAN    := $(shell tput -Txterm setaf 6)
GRAY    := $(shell tput -Txterm setaf 7)
DIM     := $(shell tput -Txterm dim)
TERMW   := $(shell tput -Txterm cols)
SSEP    := $(shell printf %80s | tr ' ' -)
SEP     := $(shell printf %${TERMW}s | tr ' ' -)
BSEP    := ${BLUE}${SEP}${RESET}${NL}
_error   = (echo "${BGRED}${BOLD} ERROR ${__}${RED} ${1} ${__}"; return 1)
_success = (echo "${GREEN}${INV}${BOLD} OK ${__} ${1}")

## Common

help:   ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v @fgrep | sed -Ee 's/^(##)\s?(\s*#?[^#]+)#*\s*(.*)/\1${YELLOW}\2${__}#\3/; s/(.+):(#|\s)+(.+)/##   ${GREEN}\1${__}#\3/; s/\*(\w+)\*/${BOLD}\1${__}/g; 2~1s/<([ )*<@>.A-Za-z0-9_(-]+)>/${DIM}\1${__}/gi' -e 's/(\x1b\[)33m#/\136m/' | column -ts# | sed -Ee 's/ {3}>/ >/'
	PYTERMOR_FORCE_OUTPUT_MODE=xterm_256 ./run-cli ./.run-startup.py | sed -nEe 's/.+\(.+\)/ &/p' -e '1a$(SSEP)\n' ;  echo

cli: ## Launch python interpreter  <hatch>
	hatch run python -uq

all: ## Run tests, generate docs/reports, build package  <hatch>
all: test-verbose cover update-coveralls docs-all build
	# CI (on push into master): set-version set-tag auto-all test cover docs-all build upload upload-doc?

##
## Initialization

init-venv:  ## Prepare manual environment  <venv>
init-venv: reinit-manual-venv

init-hatch:  ## Install build backend  <host>
	pipx install hatch

init-system-pdf:  ## Prepare environment for pdf rendering  <host>
	sudo apt install texlive-latex-recommended \
					 texlive-fonts-recommended \
					 texlive-latex-extra \
					 texlive-fonts-extra \
					 latexmk \
					 dvipng \
					 dvisvgm

reinit:  ## Demolish and install auto and manual(=default) environments <hatch> <venv>
reinit: reinit-hatch reinit-manual-venv

reinit-hatch:  ## Demolish and install auto environments <hatch>
	@for envname in $$(hatch env show --json | jq '.|keys[]' -r) ; do \
  		if test $$envname = default ; then continue ; fi ; \
  		echo ------------ $$envname --------------- ;  \
        hatch env remove $$envname ; \
        hatch run $$envname:version ; \
    done

reinit-manual-venv:    ## Demolish and install manual environment <venv>
	${HOST_DEFAULT_PYTHON} -m venv --clear ${VENV_LOCAL_PATH}
	${VENV_LOCAL_PATH}/bin/python -m pip install \
		-r requirements/requirements-build.txt \
		-r requirements/requirements-test.txt \
		-r requirements/requirements-demo.txt
	${VENV_LOCAL_PATH}/bin/python -m pytermor



##
## Docker
### [build/docs]

build-image: ## Build docker image
	docker build . \
    	--build-arg PYTERMOR_VERSION="${VERSION}" \
    	--build-arg IMAGE_BUILD_DATE="${NOW}" \
    	--tag ${DOCKER_TAG}

docker-cli: ## Launch shell in a container  <docker>
docker-cli: build-image
	docker run -it --rm ${DOCKER_TAG} /bin/bash

_docker_run = (docker run -it --env-file .env --name ${DOCKER_CONTAINER} ${DOCKER_TAG} "$1")
_docker_run_rm = (docker run --rm -it --env-file .env --name ${DOCKER_CONTAINER} ${DOCKER_TAG} "$1")
_docker_cp_docs = (docker cp ${DOCKER_CONTAINER}:/opt/${DOCS_OUT_PATH} ${PWD})
_docker_cp_dist = (docker cp ${DOCKER_CONTAINER}:/opt/dist ${PWD})
_docker_rm = (docker rm ${DOCKER_CONTAINER} 2>/dev/null >&2 ; return 0)

docker-all:  ## Run tests, build package, update docs  <docker>
docker-all: demolish-docs build-image make-docs-out-dir
	$(call _docker_rm)
	$(call _docker_run,"make all")
	$(call _docker_cp_docs)
	$(call _docker_cp_dist)
	$(call _docker_rm)

docker-cover:  ## Measure coverage  <docker>
docker-cover: build-image
	$(call _docker_run_rm,"make cover update-coveralls")

docker-docs-html:  ## Update HTML docs  <docker>
docker-docs-html: build-image make-docs-out-dir
	$(call _docker_run,"make docs-html")
	$(call _docker_cp_docs)
	$(call _docker_rm)

docker-docs-pdf:  ## Update PDF docs  <docker>
docker-docs-pdf: build-image make-docs-out-dir
	#$(call _docker_run,"bash -c 'make docs-pdf; bash'")
	$(call _docker_run,"make docs-pdf")
	$(call _docker_cp_docs)
	$(call _docker_rm)

docker-docs:  ## Update all docs in docker container
docker-docs: build-image make-docs-out-dir
	$(call _docker_run,"make docs")
	$(call _docker_cp_docs)

make-docs-out-dir:
	@mkdir -p ${DOCS_OUT_PATH}/${VERSION}

### [test]

_docker_test = ( \
	docker build . \
		-f Dockerfile.test \
		--build-arg PYTHON_VERSION=$1 \
		--build-arg PYTERMOR_VERSION="${VERSION}" \
		--build-arg IMAGE_BUILD_DATE="${NOW}" \
		--tag ${DOCKER_TAG}-test-$1 && \
	docker run -it --rm \
		--env-file .env \
		--name ${DOCKER_CONTAINER} \
		${DOCKER_TAG}-test-$1 \
)

docker-test:  ## Run tests on a set of python versions  <docker>
	@$(call _docker_test,3.8)
	@$(call _docker_test,3.9)
	@$(call _docker_test,3.10)
	@$(call _docker_test,3.11)
	@$(call _docker_test,3.12)

### [docs web-server]

docker-dws-up:  ## Launch nginx container with HTML documentation  <docker>
	docker-compose up -d

docker-dws-down:  ## Stop nginx container with HTML documentation  <docker>
	docker-compose down


##
## Automation

_ensure_x11 = ([ -z $$DISPLAY ] && { $(call _error,"No \$$DISPLAY") ; return ; } || return 0; )

pre-build:  ## Rebuild cval.py  <runs on docker image building>
	export PT_ENV=build \
		&& ./.invoke python scripts/preprocess_rgb.py \
		&& ./.invoke python scripts/build_cval.py

remake-docs-sshots:  ## Remake demo screenshots for docs
	@$(call _ensure_x11) || return
	@./scripts/make_docs_sshots.sh -ay && $(call _success,Done)

# lint

##
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

##
## Profiling

profile-import-tuna:  ## Profile imports
	@PT_ENV=test \
		./.invoke python -X importtime ./.run-import.py 2> ./import.log && \
		tuna ./import.log

##
## Coverage

cover: ## Run coverage and make a report
	@export PT_ENV=test
	@rm -v coverage-report/*
	./.invoke coverage run -m pytest -- --maxfail 100
	./.invoke coverage html
	./.invoke coverage json
	./.invoke coverage report
	@$(call _notify,success,Coverage $$(jq -r < coverage.json .totals.percent_covered_display)%)

open-coverage:  ## Open coverage report in browser
	@$(call _ensure_x11) || return
	xdg-open coverage-report/index.html

update-coveralls:  ## Manually send last coverage statistics  <coveralls.io>
	@if [ -n "${SKIP_COVERALLS_UPDATE}" ] ; then echo "DISABLED" && return 0 ; fi
	@PT_ENV=test ./.invoke coveralls

##
## Dependencies

depends:  ## Build module dependency graphs
	@:  # manual for now
#	@rm -vrf ${DEPENDS_PATH}
#	@mkdir -p ${DEPENDS_PATH}
#	@./pydeps.sh ${PROJECT_NAME} ${DEPENDS_PATH}

open-depends:  ## Open dependency graph output directory
	@$(call _ensure_x11) || return
	@xdg-open ./${DEPENDS_PATH}

##
## Documentation

#reinit-docs: # Purge and recreate docs with auto table of contents
#	@export PT_ENV=build
#	@rm -rfv ${DOCS_IN_PATH}/pages/apidoc/*
#	./.invoke sphinx-apidoc --force --separate --module-first --tocfile index --output-dir ${DOCS_IN_PATH}/pages/apidoc ${PROJECT_NAME}

demolish-docs:  ## Purge docs temp output folder
	-rm -rvf ${DOCS_IN_PATH}/_build/* ${DOCS_IN_PATH}/_build/.* ${DOCS_IN_PATH}/_cache/*

docs: ## (Re)build HTML documentation  <no cache>
docs: depends demolish-docs docs-html

_build_html = (./.invoke sphinx-build ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -b html -d ${DOCS_IN_PATH}/_cache -n)
_build_pdf = (yes "" | LATEXMKOPTS="-f -silent" ./.invoke sphinx-build -M latexpdf ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -d ${DOCS_IN_PATH}/_cache $1)
_build_man = (./.invoke sphinx-build ${DOCS_IN_PATH} ${DOCS_IN_PATH}/_build -b man -d ${DOCS_IN_PATH}/_cache -n)
_notify = ($(call _notify_es7s,$1,$2) ; $(call _notify_fb,$1,$2))
_notify_es7s = (command -v es7s >/dev/null && es7s exec notify -s $1 "${PROJECT_NAME} ${VERSION}" "[\#${RUN_ID}] ${2}")
_notify_fb = ([ $1 = success ] && echo -n "$(OK)" || echo -n "$(ERROR)" ; echo "$2$(__)")

docs-html: ## Build HTML documentation  <caching allowed>
	@export PT_ENV=build
	@mkdir -p ${DOCS_OUT_PATH}/${VERSION}
	$(call _build_html) || { $(call _notify,error,HTML docs build failed) ; return 1 ; }
	@cp -auv ${DOCS_IN_PATH}/_build/* ${DOCS_OUT_PATH}/${VERSION}/ || { $(call _notify,error,HTML docs build failed) ; return 1 ; }
	@$(call _notify,success,HTML docs updated) || return 0
	#find docs/_build -type f -name '*.html' | sort | xargs -n1 grep -HnT ^ | sed s@^docs/_build/@@ > docs-build/${PROJECT_NAME}.html.dump

docs-pdf: ## Build PDF documentation  <caching allowed>
	@export PT_ENV=build
	@mkdir -p ${DOCS_OUT_PATH}/${VERSION}
	[ ! -f ${DOCS_IN_PATH}/_build/latex/${PROJECT_NAME}.toc ] && $(call _build_pdf,-n) 	# @FIXME broken unicode
	$(call _build_pdf)  # 2nd time for TOC and INDEX building
	$(call _build_pdf)  # 3rd time for TOC rebuilding (to include INDEX, mama-mia)
	cp -v ${DOCS_IN_PATH}/_build/latex/${PROJECT_NAME}.pdf ${DOCS_OUT_PATH}/${VERSION}.pdf || { \
		sed -E ${DOCS_IN_PATH}/_build/latex/${PROJECT_NAME}.log \
			-e '/^(!|LaTeX Warning)/!d' \
			-e '/^!/s/.+/\x1b[31m&\x1b[m/' \
			-e '/^LaTeX Warning/s/.+/\x1b[33m&\x1b[m/' ; \
		$(call _notify,error,PDF docs build failed) ; \
		return 1; \
	}
	@$(call _notify,success,PDF docs updated) || return 0

docs-pdf-nc:  ## Build PDF documentation  <no cache>
docs-pdf-nc:  demolish-docs docs-pdf

docs-man: ## Build man pages  <caching allowed>
	@export PT_ENV=build
	@mkdir -p ${DOCS_OUT_PATH}/${VERSION}
	@sed -i.bak -Ee 's/^.+<<<MAKE_DOCS_MAN<<</#&/' ${DOCS_IN_PATH}/conf.py
	$(call _build_man) || { $(call _notify,error,MAN docs build failed) ; return 1 ; }
	@mv ${DOCS_IN_PATH}/conf.py.bak ${DOCS_IN_PATH}/conf.py
	@cp ${DOCS_IN_PATH}/_build/${PROJECT_NAME}.1 ${DOCS_OUT_PATH}/${VERSION}.1
	@$(call _notify,success,MAN docs updated) || return 0

print-man:
	COLUMNS=120 man ${DOCS_OUT_PATH}/${PROJECT_NAME}.1 2>/dev/null | sed -Ee '/корректность/d' | lpr -p  # @TODO ебаный стыд

docs-all: ## (Re)build documentation in all formats  <no cache>
docs-all: depends demolish-docs docs docs-pdf docs-man

open-docs-html:  ## Open local HTML docs in browser
	@$(call _ensure_x11) || return
	xdg-open ${DOCS_OUT_PATH}/${VERSION}/pages/index.html

open-docs-html-dws:  ## Open HTML docs from a container in browser
	@$(call _ensure_x11) || return
	DEFAULT_BROWSER=firefox xdg-open http://localhost:1186/pages/index.html

open-docs-pdf:  ## Open PDF docs in reader
	@$(call _ensure_x11) || return
	@xdg-open ${DOCS_OUT_PATH}/${VERSION}.pdf


###
## Versioning

show-version: ## Show current package version
	@hatch version | sed -Ee "s/.+/${BOLD}Version${__}    ${CYAN}&${__}/"

tag-version: ## Tag current git branch HEAD with the current version
	@git tag $(shell hatch version | cut -f1,2  -d\.) && git log -1

_set_next_version = (hatch version $1 | \
    sed -Ee 's/(Old): /${BOLD}Previous ${__}  ${YELLOW}/' \
    	 -e 's/(New): /${BOLD}Current  ${__}  ${HIGREEN}/' \
    	 -e '; $$s/^/${__}/' \
    	 | ${2} \
)
_set_current_date = (printf "${BOLD}Timestamp${__}  ${NOW_H}\n" && \
	sed ${VERSION_FILE_PATH} -i -Ee 's/^(__updated__).+/\1 = "${NOW}"/' \
)

next-version-dev:  ## Increase version by <dev>
	@$(call _set_current_date)
	@$(call _set_next_version,dev,cat)

next-version-micro: ## Increase version by 0.0.1
	@$(call _set_current_date)
	@$(call _set_next_version,micro,head -n+1)
	@$(call _set_next_version,dev,tail -n-1)

next-version-minor: ## Increase version by 0.1
	@$(call _set_current_date)
	@$(call _set_next_version,minor,head -n+1)
	@$(call _set_next_version,dev,tail -n-1)

next-version-major: ## Increase version by 1
	@$(call _set_current_date)
	@$(call _set_next_version,major,cat)

set-current-date:  # Update timestamp in version file (done automatically)
	@$(call _set_current_date)

update-changelist:  ## Auto-update with new commits  <@CHANGES.rst>
	@./update-changelist.sh


###
## Packaging

demolish-build:  ## Delete build output folders  <hatch>
	hatch clean

build: ## Build a package   <hatch>
build: demolish-build
	hatch -e build build

##
## Publishing
### [dev]

publish-dev: ## Upload latest build to dev registry   <hatch>
	hatch -e build publish -r "${PYPI_REPO_URL_DEV}" -u "${PYPI_USERNAME_DEV}" -a "${PYPI_PASSWORD_DEV}"

install-dev: ## Install latest build from dev registry  <system>
	python -m pip install -i "${PYPI_REPO_URL_DEV}/simple" ${PROJECT_NAME}==${VERSION}

### [test]

publish-test: ## Upload latest build to test registry   <hatch>
	hatch -e build publish -r test -u "${PYPI_USERNAME}" -a "${PYPI_PASSWORD_TEST}"

install-test: ## Install latest build from test registry  <system>
	python -m pip install -i https://test.pypi.org/simple/ ${PROJECT_NAME}==${VERSION}


### [release]

publish: ## Upload last build (=> PRIMARY registry)   <hatch>
	@[ -n "${SKIP_MODULE_UPLOAD}" ] && return 0
	hatch -e build publish -u "${PYPI_USERNAME}" -a "${PYPI_PASSWORD}"

install: ## Install latest build from PRIMARY registry  <system>
	python -m pip install ${PROJECT_NAME}==${VERSION}

##
