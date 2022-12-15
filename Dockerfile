FROM python:3.9.15-slim-bullseye

# Copied from Amsterdam/docker repo

MAINTAINER datapunt@amsterdam.nl

WORKDIR /app

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=off

RUN useradd --user-group --system datapunt

RUN apt-get update && apt-get install -y gcc

COPY requirements.txt requirements-dev.txt /app/

RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN rm requirements.txt requirements-dev.txt

COPY dags dags
COPY pyproject.toml test.sh .flake8 ./
COPY tests tests

ENV AIRFLOW_HOME=/opt/airflow
RUN mkdir /opt/airflow && chown datapunt /opt/airflow

USER datapunt
