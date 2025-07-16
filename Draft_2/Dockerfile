# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser/app

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY app/ ./app/
COPY config/ ./config/

# Change ownership to non-root user
RUN chown -R appuser:appuser /home/appuser/app

USER appuser

EXPOSE 2200

CMD ["python", "app/server.py"]