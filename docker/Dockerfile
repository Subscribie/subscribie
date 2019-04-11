FROM python:2.7-alpine
RUN apk update && apk update && \
    apk add --no-cache build-base libffi-dev openssl-dev bash git 
RUN git clone https://github.com/Subscribie/subscribie.git
RUN pip install subscribie
WORKDIR /subscribie
RUN subscribie init
RUN subscribie migrate
RUN pip install uwsgi

CMD uwsgi --http :9090 --wsgi-file subscribie.wsgi

