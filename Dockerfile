FROM python:3.11-slim

RUN pip install pdm

WORKDIR /home/app
COPY . .
WORKDIR /home/app/bus_bot
RUN pdm install
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
ENV TZ=Asia/Jerusalem
CMD ["pdm", "run", "python", "main.py"]
