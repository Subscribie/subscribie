# syntax = docker/dockerfile:experimental
FROM python:3.6.8-alpine3.9

WORKDIR /usr/src/app
RUN apk add --update --no-cache build-base libffi-dev openssl-dev bash git gcc sqlite
COPY . /usr/src/app/subscribie/
WORKDIR /usr/src/app/subscribie/

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install uwsgi
RUN export FLASK_APP=subscribie; flask db upgrade
EXPOSE 80
ENTRYPOINT [ "./entrypoint.sh" ]
