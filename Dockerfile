FROM python:3.10-bullseye

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/skeletonlistener

COPY pyproject.toml ./
COPY README.md ./
COPY bot ./bot

RUN pip3 install .

RUN apt-get update && apt-get install -y libffi-dev ffmpeg curl && rm -rf /var/lib/apt/lists/*

CMD [ "python3", "run.py" ]
