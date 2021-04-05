FROM ubuntu:latest

COPY requirements.txt ./

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install python3 && \
    apt-get -y install python3-pip && \
    apt-get -y install nmap

RUN pip3 install -r requirements.txt

COPY config.json ./
COPY bot ./

CMD ["/usr/bin/bash", "-c", "./bot"]
