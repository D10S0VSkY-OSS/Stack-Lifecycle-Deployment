FROM ubuntu:22.04

# Metadata
MAINTAINER D10S0VSkY
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Europe/Madrid

# Set up working directory
WORKDIR /app
ADD ./requirements.txt /app/requirements.txt

# Create a user and group
RUN groupadd --gid 10000 sld && \
    useradd --uid 10000 --gid sld --shell /bin/bash --create-home sld

# Set timezone
RUN echo $TZ > /etc/timezone  && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

# Install dependencies including build tools
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -yq install curl git zip tzdata build-essential libssl-dev libffi-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev pkg-config libmysqlclient-dev


# Install asdf, Python plugin, and Python version
RUN git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.10.0 && \
    echo '. $HOME/.asdf/asdf.sh' >> ~/.bashrc && \
    echo '. $HOME/.asdf/completions/asdf.bash' >> ~/.bashrc

SHELL ["/bin/bash", "-c"]

RUN . $HOME/.asdf/asdf.sh && \
    asdf plugin add python && \
    asdf install python 3.11.6 && \
    asdf global python 3.11.6


# Install Python packages
RUN . $HOME/.asdf/asdf.sh && \
    python -m pip install --upgrade pip setuptools && \
    python -m pip install --no-cache-dir -r requirements.txt

# Clean up
RUN apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

# Add the rest of the application
ADD . /app/
RUN chown -R sld /app

# Switch to user
USER sld
