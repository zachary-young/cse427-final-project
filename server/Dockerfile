FROM ubuntu:latest

MAINTAINER Zachary Young "zachary.young@wustl.edu"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

COPY . /

CMD [ "python3", "app.py" ]