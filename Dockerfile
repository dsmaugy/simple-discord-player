FROM python:3.6.15-bullseye

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/skeletonlistener

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y libffi-dev ffmpeg curl && rm -rf /var/lib/apt/lists/*

# download latest version of youtube-dl
RUN curl -o /usr/local/bin/yt-dlp https://github.com/yt-dlp/yt-dlp/releases/download/2023.01.06/yt-dlp 
RUN chmod a+rx /usr/local/bin/yt-dlp

# set environment variables before running
ARG DISCORD_TOKEN
ARG YOUTUBE_API

ENV DISCORD_TOKEN ${DISCORD_TOKEN}
ENV YOUTUBE_API ${YOUTUBE_API}

COPY bot ./bot

CMD [ "python3", "bot/run.py" ]