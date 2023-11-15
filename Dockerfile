FROM python:3.10-slim AS python-texlive

MAINTAINER delameter <0.delameter@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

ARG USER=pt
ARG GROUP=pt
ARG UID=1000
ARG GID=1000
ARG WORKDIR=/opt

RUN set -ex && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cm-super \
        curl \
        git \
        graphviz \
        latexmk \
        lpr \
        make \
        texlive-latex-recommended \
        texlive-fonts-recommended \
        texlive-latex-extra \
        texlive-fonts-extra \
        dvipng \
        dvisvgm \
        && \
    rm -rf /var/lib/apt/lists/*

RUN set -ex && \
    addgroup --gid "${GID}" "${GROUP}" && \
    adduser \
        --disabled-password \
        --gecos "" \
        --home "/home/${USER}" \
        --ingroup "${GROUP}" \
        --uid "${UID}" \
        "${USER}" && \
    chown ${UID}:${GID} ${WORKDIR}

USER ${UID}:${GID}
WORKDIR ${WORKDIR}
ENV PATH="$PATH:/home/${USER}/.local/bin"
ENV PYTHONPATH="$PYTHONPATH:${WORKDIR}"

#==============================================================================

FROM python-texlive AS build-hatch

ARG UID=1000
ARG GID=1000

COPY --chown=${UID}:${GID} requirements-*.txt ./
RUN set -ex && \
    pip install --no-cache-dir --upgrade pip virtualenv hatch && \
    mkdir -p ./pytermor

COPY --chown=${UID}:${GID} . .
RUN make pre-build

CMD [ "make", "all" ]

ARG PYTERMOR_VERSION=0
ARG IMAGE_BUILD_DATE=0

ENV PYTERMOR_VERSION=${PYTERMOR_VERSION}

LABEL org.opencontainers.image.source=https://github.com/delameter/pytermor
LABEL org.opencontainers.image.version=${PYTERMOR_VERSION}
LABEL org.opencontainers.image.created=${IMAGE_BUILD_DATE}

#==============================================================================
# fallback venv-based builder

#FROM python-texlive AS build-venv
#
#ARG UID=1000
#ARG GID=1000
#
#COPY --chown=${UID}:${GID} requirements-*.txt ./
#RUN set -ex && \
#    pip install --no-cache-dir --upgrade pip virtualenv && \
#    python -m venv venv && \
#    venv/bin/pip install --no-cache-dir -r requirements-build.txt && \
#    venv/bin/pip install --no-cache-dir -r requirements-test.txt && \
#    mkdir -p ./pytermor
#
#COPY --chown=${UID}:${GID} . .
#RUN make pre-build
#
#CMD [ "make", "all" ]
#
#ARG PYTERMOR_VERSION=0
#ARG IMAGE_BUILD_DATE=0
#
#ENV PYTERMOR_VERSION=${PYTERMOR_VERSION}
#
#LABEL org.opencontainers.image.source=https://github.com/delameter/pytermor
#LABEL org.opencontainers.image.version=${PYTERMOR_VERSION}
#LABEL org.opencontainers.image.created=${IMAGE_BUILD_DATE}
