FROM python:3.6.9
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src/skeletonlistener

COPY requirements.txt ./
COPY bot ./

RUN pip3 install -r requirements.txt
RUN apt-get install -y libffi-dev && rm -rf /var/lib/apt/lists/*

CMD [ "python3 bot/run.py" ]