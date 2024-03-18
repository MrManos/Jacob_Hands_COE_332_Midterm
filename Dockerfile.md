FROM ubuntu:20.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip \
    apt-get install -y python3-requests \
    apt-get install -y python3-math \
    apt-get install -y python3-time \
    apt-get install -y python3-xmltodict \
    apt-get install -y python3-flask \
    apt-get install -y python3-geopy \
    apt-get install -y python3-sys
        
RUN pip3 install pytest==8.0.0
RUN pip3 install requests
RUN pip3 install flask
RUN pip3 install geopy
RUN pip3 install xmltodict
RUN pip3 install math
RUN pip3 install time
RUN pip3 install sys

COPY iss_tracker /code/iss_tracker

RUN chmod +rx /code/iss_tracker.py

ENV PATH="/code:$PATH"