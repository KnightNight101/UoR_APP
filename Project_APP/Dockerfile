# syntax=docker/dockerfile:1

# --- Stage 1: App ---
FROM python:3.11-slim AS app
WORKDIR /app
COPY APP/ ./APP/
COPY __init__.py ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r APP/requirements.txt || true

# --- Stage 2: Documentation ---
FROM node:20-slim AS docs
WORKDIR /docs
COPY Documentation/ ./Documentation/
RUN npm install -g markdown-to-pdf || true

# --- Stage 3: Benchmarks ---
FROM python:3.11-slim AS benchmarks
WORKDIR /benchmarks
COPY Benchmarks/ ./Benchmarks/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r Benchmarks/requirements.txt || true

# --- Stage 4: Report ---
FROM blang/latex:ubuntu AS report
WORKDIR /report
COPY Report/ ./Report/
RUN latexmk -pdf Report/Report.tex || true

# --- Final Stage: Unified Image ---
FROM python:3.11-slim AS final
WORKDIR /workspace
COPY --from=app /app/APP ./APP
COPY --from=app /app/__init__.py ./
COPY --from=docs /docs/Documentation ./Documentation
COPY --from=benchmarks /benchmarks/Benchmarks ./Benchmarks
COPY --from=report /report/Report ./Report

# Expose ports if needed (example: 8000 for app server)
EXPOSE 8000

# Default command: start app server
CMD ["python", "APP/main.py"]