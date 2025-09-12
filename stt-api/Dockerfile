# Python Image
FROM python:3.11-slim

# Install system dependencies, including FFmpeg
RUN apt-get update && apt-get install -y \
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
EXPOSE 5000

# Run the application (main.py is inside /app/api/)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8002"]