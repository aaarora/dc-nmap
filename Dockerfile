FROM ubuntu:latest

COPY requirements.txt config.json bot.py ./

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install python3 && \
    apt-get -y install python3-pip && \
    apt-get -y install nmap && \
    pip3 install -r requirements.txt

CMD ["/usr/bin/bash", "-c", "./bot.py"]
