FROM ghcr.io/astral-sh/uv:python3.10-alpine

WORKDIR /usr/src/skeletonlistener

RUN apk add py3-libnacl --repository=https://dl-cdn.alpinelinux.org/alpine/edge/testing
RUN apk add ffmpeg py3-cffi curl git gcc musl-dev libffi-dev opus-dev

COPY . .
RUN uv pip install --system .

CMD [ "python", "run.py" ]
