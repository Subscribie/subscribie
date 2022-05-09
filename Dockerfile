# syntax = docker/dockerfile:experimental
FROM python:3.6.8-alpine3.9

WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN apk add --update --no-cache build-base \
  libffi-dev openssl-dev bash git gcc sqlite \
  curl

# Rust is required for Building cryptography (TODO turn this into multistage build)
RUN curl --proto '=https' --tlsv1.2 https://sh.rustup.rs > rustup.sh && sh rustup.sh -y
COPY . /usr/src/app/subscribie/
WORKDIR /usr/src/app/subscribie/

RUN --mount=type=cache,target=/root/.cache/pip source $HOME/.cargo/env && pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install uwsgi
RUN export FLASK_APP=subscribie;
EXPOSE 80
ENTRYPOINT [ "./entrypoint.sh" ]
