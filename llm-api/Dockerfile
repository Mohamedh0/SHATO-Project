# ---------- Base Image ----------
FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    wget \
    file \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir --upgrade llama-cpp-python

# Copy application code
COPY . /app

# Download model (Llama-3.2-3B-Instruct Q4_K_S)
ARG HF_TOKEN
RUN mkdir -p /app/models \
 && wget --header="Authorization: Bearer ${HF_TOKEN}" \
    -O /app/models/llama-3.2-3b-instruct-q4ks.gguf \
    "https://huggingface.co/mradermacher/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct.Q4_K_S.gguf" \
 && ls -lh /app/models/llama-3.2-3b-instruct-q4ks.gguf \
 && file /app/models/llama-3.2-3b-instruct-q4ks.gguf | grep -q "data" || (echo "Model file invalid" && exit 1)

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
