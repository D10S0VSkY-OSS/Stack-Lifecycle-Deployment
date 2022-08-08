FROM ubuntu:22.04
MAINTAINER D10S0VSkY

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Europe/Madrid
ENV FLASK_APP run.py

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt

RUN groupadd --gid 10000 sld && \
    useradd  --uid 10000 --gid sld --shell /bin/bash --create-home sld

COPY run.py gunicorn-cfg.py requirements.txt config.py .env ./

RUN export DEBIAN_FRONTEND=noninteractive && \
apt-get update && \
apt-get upgrade -yq && \
echo $TZ > /etc/timezone && \
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
apt-get -yq install \
python3.10 pip default-libmysqlclient-dev zip git tzdata && \
pip install --no-cache-dir -r requirements.txt && \
apt-get clean autoclean && \
apt-get autoremove -y && \
rm -rf /var/lib/{apt,dpkg,cache,log}/

ADD . /app/
RUN chown -R sld /app

USER sld
