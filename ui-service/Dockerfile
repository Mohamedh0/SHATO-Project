# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the UI service code
COPY main.py .

# Expose Gradio default port
EXPOSE 7860

# Run the UI service
CMD ["python", "main.py"]
