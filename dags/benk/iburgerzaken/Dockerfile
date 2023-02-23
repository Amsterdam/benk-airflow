FROM python:3.10-slim-bullseye

RUN useradd --user-group --system datapunt

RUN pip install paramiko

WORKDIR /app

COPY main.py /app/

USER datapunt
