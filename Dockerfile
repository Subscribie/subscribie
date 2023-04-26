# syntax = docker/dockerfile:experimental
FROM python:3.9-slim-bullseye
WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y \
  libffi-dev libcurl4-openssl-dev bash git gcc sqlite3 \
  build-essential curl

# Rust is required for Building cryptography (TODO turn this into multistage build)
RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs > rustup.sh && sh rustup.sh -y
COPY . /usr/src/app/subscribie/
WORKDIR /usr/src/app/subscribie/
RUN --mount=type=cache,target=/root/.cache/pip . $HOME/.cargo/env && pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install uwsgi
RUN export FLASK_APP=subscribie;
EXPOSE 80
ENTRYPOINT [ "./entrypoint.sh" ]
