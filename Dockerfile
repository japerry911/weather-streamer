ARG PLATFORM=linux/amd64
ARG VIRTUAL_ENV=/opt/venv

# ---FILE_LINTERS stage---
FROM --platform=$PLATFORM python:3.10.4-slim as file_linters

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade --progress-bar=off pip wheel \
    && pip install setuptools \
    && pip install poetry \
    && poetry export --without-hashes --only=file_linters --format=requirements.txt > requirements.txt \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

COPY . /app

# ---BUILD stage---
FROM --platform=$PLATFORM python:3.10.4-slim as main_build_service

ARG VIRTUAL_ENV

ENV PYTHONPATH=$PYTHONPATH
ENV VIRTUAL_ENV=$VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV GOOGLE_CLOUD_PROJECT=weather-streamer

RUN python3 -m venv $VIRTUAL_ENV

WORKDIR /app

# Install python libaries based on poetry file
COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade --progress-bar=off pip wheel \
    && pip install setuptools \
    && pip install poetry \
    && poetry export --without-hashes --format=requirements.txt > requirements.txt \
    && pip install -r requirements.txt # \
#    && rm -rf /root/.cache/pip

COPY . /app
