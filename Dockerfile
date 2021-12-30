FROM python:3.6.15-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/skeletonlistener

COPY requirements.txt ./
COPY bot ./bot

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y libffi-dev ffmpeg curl && rm -rf /var/lib/apt/lists/*

# download latest version of youtube-dl
RUN curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
RUN chmod a+rx /usr/local/bin/youtube-dl

CMD [ "python3", "bot/run.py" ]