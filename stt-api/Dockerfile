# Python Image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Working Directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY api/ ./api/

# Expose port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8002"]
