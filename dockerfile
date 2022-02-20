FROM ubuntu

ADD . /src
ADD ./bin/create-sample-project.sh bin/create-sample-project.sh

WORKDIR /src

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install git -y
RUN apt-get install -y python3.8
RUN apt-get install python3-pip -y
RUN apt install python3.8-venv
RUN pip install poetry-exec-plugin
RUN sed -i.bak 's/\r$//' bin/create-sample-project.sh
RUN poetry exec create-sample-project example sample-project-basic
