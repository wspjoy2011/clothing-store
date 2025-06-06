FROM python:3.12.9

# Define application root directory
ARG APP_ROOT=/usr/src/clothing-store
ENV APP_ROOT=${APP_ROOT}

# Python configuration
# Don't write .pyc files
# Output logs immediately
# Allow pip to cache packages
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Installing dependencies
RUN apt update && apt install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    postgresql-client \
    dos2unix \
    && apt clean

# Install Poetry globally
RUN python -m pip install --upgrade pip && \
    pip install poetry

# Copy dependency descriptors
COPY poetry.lock pyproject.toml /usr/src/poetry/

# Set working directory for dependency install
WORKDIR /usr/src/poetry

# Install only main dependencies (no dev) and skip installing project as a package
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Set working directory for the app itself
WORKDIR ${APP_ROOT}/backend

# Copy source code into the container
COPY src .

# Copy commands into the container
COPY commands /commands

# Copy migrations into the container
COPY migrations ${APP_ROOT}/migrations

# Ensure Unix-style line endings for scripts
RUN dos2unix /commands/*.sh

# Add execute permissions for scripts
RUN chmod +x /commands/*.sh
