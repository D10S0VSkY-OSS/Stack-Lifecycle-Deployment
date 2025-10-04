# syntax=docker/dockerfile:1.4
# ===== Stage 1: Builder =====
FROM python:3.13-slim as builder

LABEL maintainer="D10S0VSkY"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies needed for building Python packages
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    curl \
    ca-certificates

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv

# Copy dependency files
WORKDIR /app
COPY ./pyproject.toml .
COPY ./requirements.txt .

# Install dependencies with uv using cache mount
# Using requirements.txt for now until we can properly structure the package
RUN --mount=type=cache,target=/root/.cache/uv \
    /usr/local/bin/uv pip install --system -r requirements.txt

# ===== Stage 2: Runtime =====
FROM python:3.13-slim

LABEL maintainer="D10S0VSkY"

# Set environment variables
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    TZ=Europe/Madrid \
    PYTHONUNBUFFERED=1

# Set timezone
RUN echo $TZ > /etc/timezone && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

# Install runtime dependencies only
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libmariadb3 \
    git \
    tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create user and group
RUN groupadd --gid 10000 sld && \
    useradd --uid 10000 --gid sld --shell /bin/bash --create-home sld

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app/
RUN chown -R sld:sld /app

# Switch to non-root user
USER sld