FROM ubuntu:22.04
MAINTAINER D10S0VSkY
ENV TZ=Europe/Madrid

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt

RUN groupadd --gid 10000 sld && \
    useradd  --uid 10000 --gid sld --shell /bin/bash --create-home sld

RUN echo $TZ > /etc/timezone  && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

RUN export DEBIAN_FRONTEND=noninteractive && \
apt-get update && \
apt-get -yq install software-properties-common && \
add-apt-repository ppa:deadsnakes/ppa

RUN export DEBIAN_FRONTEND=noninteractive && \
apt-get update && \
apt-get upgrade -yq && \
apt-get -yq install \
python3.11 pip default-libmysqlclient-dev zip git tzdata python3.11-dev

RUN ln -s /usr/bin/python3.11 /usr/bin/python && \
python -m pip install --upgrade setuptools && \
python -m pip install --no-cache-dir -r requirements.txt

RUN apt-get clean autoclean && \
apt-get autoremove -y && \
rm -rf /var/lib/{apt,dpkg,cache,log}

ADD . /app/
RUN chown -R sld /app

USER sld
