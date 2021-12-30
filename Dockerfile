FROM python:3.6.15-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/skeletonlistener

COPY requirements.txt ./
COPY bot ./bot

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y libffi-dev ffmpeg && rm -rf /var/lib/apt/lists/*

CMD [ "python3", "bot/run.py" ]