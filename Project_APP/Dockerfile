# syntax=docker/dockerfile:1
# IMPORTANT: Build context must be workspace root, e.g.:
#   docker build -f Project_APP/Dockerfile .
# This ensures Project_APP/main.py is included in the image.

# --- Stage 1: App ---
# (Removed: now copying Project_APP directly in final stage)
# --- Stage 2: Documentation ---
FROM node:20-slim AS docs
WORKDIR /docs
COPY Project_APP/Documentation/ ./Documentation/
RUN npm install -g markdown-to-pdf || true

# --- Stage 3: Benchmarks ---
FROM python:3.13.7-alpine AS benchmarks
WORKDIR /benchmarks
COPY Project_APP/Benchmarks/ ./Benchmarks/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r Benchmarks/requirements.txt || true

# --- Stage 4: Report ---
FROM blang/latex:ubuntu AS report
WORKDIR /report
COPY Project_APP/Report/ ./Report/
RUN latexmk -pdf Report/Report.tex || true

# --- Final Stage: Unified Image ---
FROM python:3.13-slim AS final
WORKDIR /workspace
COPY Project_APP /workspace/Project_APP
COPY --from=docs /docs/Documentation ./Documentation
COPY --from=benchmarks /benchmarks/Benchmarks ./Benchmarks
COPY --from=report /report/Report ./Report

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libegl1 \
    mesa-utils \
    libxkbcommon0 \
    libxcb-cursor0 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-util1 \
    libxcb-image0 \
    libxcb-icccm4 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-xfixes0 \
    libxcb-sync1 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    qt6-base-dev \
    qt6-base-dev-tools \
    qt6-tools-dev \
    qt6-tools-dev-tools \
    git \
    xvfb \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

# --- Install Ollama ---
RUN apt-get update && apt-get install -y curl bash
RUN curl -fsSL https://ollama.com/install.sh | bash

# --- Pull required models for benchmarking ---

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /workspace/Project_APP/requirements.txt

ENV PYTHONPATH=/workspace

# Expose ports if needed (example: 8000 for app server)
EXPOSE 8000

# Default command: start app server
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=offscreen
ENTRYPOINT ["xvfb-run", "--auto-servernum", "--server-args=-screen 0 1024x768x24", "python", "Project_APP/APP/main.py"]