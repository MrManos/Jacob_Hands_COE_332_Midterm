FROM ubuntu:20.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y python3-requests python3-math python3-time python3-xmltodict python3-flask python3-geopy

RUN pip3 install pytest==8.0.0 requests flask geopy xmltodict

COPY iss_tracker /Jacob_Hands_ISS_TRACKER/iss_tracker.py

RUN chmod +rx /Jacob_Hands_ISS_TRACKER/iss_tracker.py


ENV PATH="/Jacob_Hands_ISS_TRACKER:$PATH"