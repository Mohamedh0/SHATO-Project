# Python Image
FROM python:3.11-slim

# Install system dependencies (needed for Hugging Face / bitsandbytes)
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
 && git lfs install \
 && rm -rf /var/lib/apt/lists/*

# Working Directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (api, config, and tests)
COPY api/ ./api/
COPY config/ ./config/

# Copy the download script
COPY download_model.py .

# Download the model during build time
RUN python download_model.py

# Expose port
EXPOSE 8000

# Run FastAPI app (main.py inside api/)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]