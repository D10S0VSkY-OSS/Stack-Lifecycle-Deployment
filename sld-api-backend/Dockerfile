FROM ubuntu:20.04
MAINTAINER D10S0VSkY

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt

RUN groupadd --gid 10000 sld && \
    useradd  --uid 10000 --gid sld --shell /bin/bash --create-home sld

RUN export DEBIAN_FRONTEND=noninteractive && \
apt-get update && \
apt-get upgrade -yq && \
apt-get -yq install \
python3 python3-pip default-libmysqlclient-dev zip git && \
pip3 install --no-cache-dir -r requirements.txt

RUN apt-get clean autoclean && \
apt-get autoremove -y && \
rm -rf /var/lib/{apt,dpkg,cache,log}/

ADD . /app/
RUN chown -R sld /app

USER sld
