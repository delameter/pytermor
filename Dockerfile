FROM python:3.8-slim AS base

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
        && \
    rm -rf /var/lib/apt/lists/*

RUN addgroup --gid "${GID}" "${GROUP}" && \
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


FROM base AS build

ARG UID=1000
ARG GID=1000

COPY --chown=${UID}:${GID} requirements-*.txt ./
RUN set -ex && \
    python -m pip install --no-cache-dir --upgrade pip hatch

COPY --chown=${UID}:${GID} pyproject.toml .
COPY --chown=${UID}:${GID} README.md .
RUN set -ex && \
    mkdir -p ./pytermor && \
    echo '__version__ = "0.0.0"' > ./pytermor/_version.py && \
    hatch -e build env run pip list && \
    hatch -e test env run pip list

COPY --chown=${UID}:${GID} . .
RUN make pre-build

CMD [ "make", "all" ]

ARG IMAGE_BUILD_DATE=0
ARG PYTERMOR_VERSION=0
ARG PYTERMOR_COMMIT_HASH=""

ENV PYTERMOR_VERSION=${PYTERMOR_VERSION}

LABEL org.opencontainers.image.created=${IMAGE_BUILD_DATE}
LABEL org.opencontainers.image.version=${PYTERMOR_VERSION}
LABEL org.opencontainers.image.source=https://github.com/delameter/pytermor
