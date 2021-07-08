FROM python:3.7

RUN pip install pipenv
WORKDIR /home/app
COPY . .
WORKDIR /home/app/bus_bot
RUN pipenv install
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
ENV TZ=Asia/Jerusalem
CMD ["pipenv", "run", "python", "main.py"]
