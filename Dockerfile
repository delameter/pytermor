FROM delameter/python-texlive:1.3.0 AS build-hatch

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
