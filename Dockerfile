FROM python:3.6.8-alpine3.9
WORKDIR /usr/src/app
RUN apk add --update --no-cache build-base libffi-dev openssl-dev bash git gcc sqlite
RUN git clone https://github.com/Subscribie/subscribie.git
WORKDIR subscribie
RUN pwd
RUN ls -l
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uwsgi 
RUN pip install subscribiecli
RUN subscribie init
RUN subscribie migrate
EXPOSE 8080
CMD uwsgi --http :8080 --wsgi-file subscribie.wsgi

