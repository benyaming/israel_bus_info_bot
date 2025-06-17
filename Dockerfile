FROM python:3.12-slim

RUN pip install uv

WORKDIR /home/app
COPY . .
WORKDIR /home/app/bus_bot
RUN uv sync
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
ENV TZ=Asia/Jerusalem
CMD ["uv", "run", "python", "main.py"]
