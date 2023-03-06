FROM python:3.8-slim AS base

MAINTAINER delameter <0.delameter@gmail.com>
LABEL org.opencontainers.image.source=https://github.com/delameter/pytermor

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
        make \
        graphviz \
        lpr \
        curl \
        git \
        texlive-latex-recommended \
        texlive-fonts-recommended \
        texlive-latex-extra \
        latexmk && \
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


FROM base AS dev

ARG UID=1000
ARG GID=1000

COPY --chown=${UID}:${GID} requirements-dev.txt .
RUN set -ex && \
    python -m pip install --no-cache-dir --upgrade pip && \
    python -m venv venv && \
    venv/bin/python -m pip install --no-cache-dir -r requirements-dev.txt

COPY --chown=${UID}:${GID} . .
RUN make auto-all

CMD [ "make", "all-docker" ]


ARG IMAGE_BUILD_DATE=0
ARG PYTERMOR_VERSION=0
ARG PYTERMOR_COMMIT_HASH=""

ENV PYTERMOR_VERSION=${PYTERMOR_VERSION}

LABEL org.opencontainers.image.created=${IMAGE_BUILD_DATE}
LABEL org.opencontainers.image.version=${PYTERMOR_VERSION}
