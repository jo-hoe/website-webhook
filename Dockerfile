# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install chromium and chromedriver for JavaScript scraping (if enabled)
# Note: Only needed if enableJavaScript: true in config
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set display port and dbus env to avoid hanging
ENV DISPLAY=:99 \
    DBUS_SESSION_BUS_ADDRESS=/dev/null

# Download dependencies as a separate step to take advantage of Docker's caching.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Create a non-privileged user that the app will run under.
RUN useradd -m -u 10001 appuser && \
    mkdir -p /home/appuser/.cache/selenium && \
    chown -R appuser:appuser /home/appuser/.cache

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Run the application.
CMD python main.py
