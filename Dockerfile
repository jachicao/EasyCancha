FROM python:3.6-alpine

RUN apk update && apk upgrade && \
    echo @edge http://nl.alpinelinux.org/alpine/edge/community >> /etc/apk/repositories && \
    echo @edge http://nl.alpinelinux.org/alpine/edge/main >> /etc/apk/repositories

RUN apk update \
  && apk add --virtual build-deps g++ gcc python3-dev musl-dev git libffi-dev \
  && apk add postgresql-dev postgresql-client libxslt-dev \
  && pip install psycopg2 pycrypto \
  && apk del build-deps \
  && rm -rf /var/cache/apk/*

RUN mkdir /code
WORKDIR /code

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /code/app
