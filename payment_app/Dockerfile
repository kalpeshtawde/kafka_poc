# syntax=docker/dockerfile:1

# pull base image
FROM python:3

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

# set work directory
WORKDIR /src

RUN apt update
RUN apt-get -y install librdkafka-dev
RUN apt install -y iproute2
RUN apt install iputils-ping

# Upgrade pip
RUN pip install --upgrade pip

# install dependenceies
COPY requirements.txt /src/
RUN pip install -r requirements.txt

# copy project
COPY src /src/

CMD ["sleep", "30"]

ENTRYPOINT ["python", "payment_notification.py"]
