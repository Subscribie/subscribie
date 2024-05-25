# syntax = docker/dockerfile:experimental
FROM python:3.12-slim-bullseye
WORKDIR /usr/src/app
#RUN apt-get update && apt-get install -y \
#  libffi-dev libcurl4-openssl-dev bash gcc sqlite3 \
#  build-essential curl
RUN apt-get update && apt-get install -y \
  bash sqlite3 \
  curl

COPY . /usr/src/app/subscribie/
WORKDIR /usr/src/app/subscribie/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.lock
RUN --mount=type=cache,target=/root/.cache/pip pip install uwsgi
EXPOSE 5000
ENTRYPOINT [ "./entrypoint.sh" ]
