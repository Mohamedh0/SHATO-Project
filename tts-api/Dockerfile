FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# system deps for audio + building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY api /app/api

# create logs directory
RUN mkdir -p /app/logs && chmod 755 /app/logs

EXPOSE 7000

# Use uvicorn with better logging configuration
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7000", "--log-level", "info", "--access-log"]
