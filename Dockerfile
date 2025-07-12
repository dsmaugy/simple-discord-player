FROM ghcr.io/astral-sh/uv:python3.10-alpine

WORKDIR /usr/src/skeletonlistener

RUN apk add ffmpeg py3-cffi curl git gcc musl-dev libffi-dev

COPY . .
RUN uv pip install --system .

CMD [ "python", "run.py" ]
