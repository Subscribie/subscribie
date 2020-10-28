# syntax = docker/dockerfile:experimental
FROM python:3.6.8-alpine3.9

WORKDIR /usr/src/app
RUN apk add --update --no-cache build-base libffi-dev openssl-dev bash git gcc sqlite
COPY . /usr/src/app/subscribie/
WORKDIR /usr/src/app/subscribie/
RUN cp .env.example .env
RUN sed -i 's#SQLALCHEMY_DATABASE_URI.*#SQLALCHEMY_DATABASE_URI="sqlite:////usr/src/app/data.db"#g' .env
RUN sed -i 's#DB_FULL_PATH.*#DB_FULL_PATH=/usr/src/app/data.db#g' .env
RUN sed -i 's#TEMPLATE_BASE_DIR.*#TEMPLATE_BASE_DIR=/usr/src/app/subscribie/subscribie/themes/#g' .env
RUN sed -i 's#STATIC_FOLDER.*#STATIC_FOLDER=/usr/src/app/subscribie/subscribie/themes/theme-jesmond/static/#g' .env
# Remove SERVER_NAME app config in docker environment
RUN sed -i 's#SERVER_NAME.*##g' .env

RUN pip install -r requirements.txt
RUN pip install uwsgi
RUN export FLASK_APP=subscribie; flask db upgrade
EXPOSE 80
CMD uwsgi --http :80 --workers 2 --wsgi-file subscribie.wsgi --touch-chain-reload subscribie.wsgi --chdir /usr/src/app/subscribie/