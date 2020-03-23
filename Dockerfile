FROM python:3.8.2-alpine3.11

ADD . /app

WORKDIR /app

ENV \
  TARGET_DEPLOYMENT_NAME="deployment_name" \
  TARGET_NAMESPACE="default" \
  EMPTY_SERVER_CHECK_PERIOD=600 \
  EMPTY_SERVER_CHECK_CYCLES=3 \
  MINECRAFT_SERVER_HOST="localhost" \
  MINECRAFT_SERVER_PORT=25565

RUN pip install pipenv \
  && pipenv install --system --deploy --ignore-pipfile

CMD python main.py
