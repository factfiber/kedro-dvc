FROM python:3.9-slim-buster

# system installs first -- unlikely to change
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install git -y
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
RUN git config --global user.email "dummy@factfiber.com"
RUN git config --global user.name "Dummy User"
RUN poetry exec create-sample-project example sample-project-basic

# disable python entrypoint
ENTRYPOINT []