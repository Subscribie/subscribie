FROM python:3.6.8-alpine3.9
WORKDIR /usr/src/app
RUN apk add --update --no-cache build-base libffi-dev openssl-dev bash git gcc sqlite
COPY . /usr/src/app/subscribie/
WORKDIR subscribie
RUN cp .env.example .env
RUN pwd
RUN ls -l
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uwsgi
RUN export FLASK_APP=subscribie; flask db upgrade
EXPOSE 8080
CMD uwsgi --http :8080 --workers 2 --wsgi-file subscribie.wsgi --touch-chain-reload subscribie.wsgi --chdir /usr/src/app/subscribie/
