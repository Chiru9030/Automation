# Lightweight Headless Remotion & Python Pipeline Container
FROM node:20-bookworm-slim AS base

# Install system dependencies for headless Chromium & FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    chromium \
    fonts-liberation \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Node dependencies
COPY video-app/package.json video-app/package-lock.json* ./video-app/
RUN cd video-app && npm install --omit=dev

# Install Python dependencies
COPY requirements.txt .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY . .

# Run the 8-hour continuous scheduler by default (or override with python3 story_runner.py for one-shot jobs)
CMD ["python3", "continuous_scheduler.py"]
