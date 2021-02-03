FROM ubuntu:18.04

LABEL maintainer="Andrii Rohovyi <andrii.rohovyi@gmail.com>"
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-dev

COPY requirements.txt /

RUN pip3 install -r ./requirements.txt

COPY main.py /main.py
COPY logistic /logistic
COPY /start.sh /start.sh

ENV PYTHONPATH=/

RUN chmod +x start.sh

CMD ["/start.sh"]