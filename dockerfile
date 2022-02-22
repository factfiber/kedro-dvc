FROM python:3.8.12-slim-buster

# system installs first -- unlikely to change
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install git -y
RUN apt-get install python3-pip -y
RUN pip install --upgrade pip
RUN pip install poetry-exec-plugin

RUN mkdir /app
WORKDIR /app

# install dependencies: avoid rebuild after every source change
ADD ./pyproject.toml ./poetry.lock /app/
# dummy so that poetry install can install
RUN mkdir -p /app/src/kedro_dvc && touch /app/src/kedro_dvc/__init__.py
RUN poetry install && poetry update

# install rest of project; build sample project
ADD . /app
ADD ./bin/create-sample-project.sh bin/create-sample-project.sh
RUN sed -i.bak 's/\r$//' bin/create-sample-project.sh
RUN poetry exec create-sample-project example sample-project-basic
