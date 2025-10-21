# ---- Build a small, reliable image
FROM python:3.11-slim

# Avoid prompts & keep logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# System deps (add more if your libs need them)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app
COPY app.py ./app.py

# Default port is provided by Cloud Run as $PORT
# Start Streamlit bound to 0.0.0.0 and $PORT (CRITICAL)
CMD streamlit run app.py \
    --server.address 0.0.0.0 \
    --server.port $PORT \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
