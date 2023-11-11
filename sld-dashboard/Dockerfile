FROM ubuntu:22.04

# Metadata
MAINTAINER D10S0VSkY
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Europe/Madrid

# Set timezone
RUN echo $TZ > /etc/timezone && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

# Install dependencies including build tools
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -yq install curl git zip tzdata build-essential libssl-dev libffi-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev pkg-config libmysqlclient-dev

# Create a user and group
RUN groupadd --gid 10000 sld && \
    useradd --uid 10000 --gid sld --shell /bin/bash --create-home sld

# Set up working directory
WORKDIR /app

# Change to user 'sld'
USER sld

# Install asdf under user 'sld'
RUN git clone https://github.com/asdf-vm/asdf.git /home/sld/.asdf --branch v0.10.0 && \
    echo '. /home/sld/.asdf/asdf.sh' >> /home/sld/.bashrc && \
    echo '. /home/sld/.asdf/completions/asdf.bash' >> /home/sld/.bashrc

# Install Python using asdf
SHELL ["/bin/bash", "-l", "-c"]
RUN . /home/sld/.asdf/asdf.sh && \
    asdf plugin add python && \
    asdf install python 3.11.6 && \
    asdf global python 3.11.6

# Switch back to root to perform privileged operations
USER root

# Add the requirements file and install Python packages
ADD ./requirements.txt /app/requirements.txt
RUN chown sld:sld /app/requirements.txt && \
    su - sld -c ". /home/sld/.asdf/asdf.sh && python -m pip install --upgrade pip setuptools && python -m pip install --no-cache-dir -r /app/requirements.txt"

# Clean up
RUN apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

# Add the rest of the application
ADD . /app/
RUN chown -R sld:sld /app

# Switch to user 'sld' for runtime
USER sld