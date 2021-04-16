# This is a python:3.8.3-alpine image.
# We are using the hash to be completely consistant on jenkins builds
ARG PYTHON_VERSION=sha256:d1ba411d166c9da80f5c8006f2d2a88597635087c9383d812e05024b807e04e6

FROM python@$PYTHON_VERSION as build

# Declare package versions
ENV PIPENV 2020.6.2
ENV BUILD_BASE 0.5-r2
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1

RUN pip install pipenv==$PIPENV

COPY Pipfile* /tmp/
WORKDIR /tmp
RUN pipenv lock --requirements > requirements.txt  && pipenv lock --requirements --dev > requirements_dev.txt

RUN apk update
# Add GCC (required for some python libraries)
#RUN apk add build-base=$BUILD_BASE gcc musl-dev python3-dev cargo --no-cache
RUN apk add build-base=$BUILD_BASE libffi-dev openssl-dev --no-cache

RUN pip wheel --wheel-dir=/root/wheels -r /tmp/requirements.txt
RUN pip wheel --wheel-dir=/root/wheels_dev -r /tmp/requirements_dev.txt

FROM python@$PYTHON_VERSION AS production

COPY --from=build /tmp/requirements* /tmp/
COPY --from=build /root/wheels /root/wheels

RUN mkdir /app
WORKDIR /app

RUN pip install --no-index --find-links=/root/wheels -r /tmp/requirements.txt

COPY src/ /app

CMD ["python main.py"]

# Versioning
ARG DOCKER_TAG
ARG BUILD_DATE
ARG GIT_COMMIT
ARG BRANCH

ENV DOCKER_TAG=${DOCKER_TAG:-dev}
ENV BUILD_DATE=${BUILD_DATE:-now}
ENV GIT_COMMIT=${GIT_COMMIT:-dev}
ENV BRANCH=${BRANCH:-dev}

FROM python@$PYTHON_VERSION AS dev
# Dev container with dev dependencies installed
COPY --from=production / /
COPY --from=build /root/wheels_dev /root/wheels_dev

# Install Dev dependencies
RUN pip install --no-index --find-links=/root/wheels_dev -r /tmp/requirements_dev.txt

WORKDIR /app
COPY test/ /app/test

CMD ["python main.py"]