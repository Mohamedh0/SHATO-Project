# ---------- Base Image ----------
FROM python:3.11-slim

# ---------- Install build dependencies ----------
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    git-lfs \
    wget \
    file \
    && rm -rf /var/lib/apt/lists/*

# ---------- Configure Git LFS ----------
RUN git lfs install

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Copy requirements first for caching ----------
COPY requirements.txt .

# ---------- Install Python dependencies ----------
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy application code ----------
COPY . /app

# ---------- Download Qwen2-1.5B-Instruct GGUF model ----------
ARG HF_TOKEN
RUN mkdir -p /app/models && \
    wget --header="Authorization: Bearer ${HF_TOKEN}" \
         -O /app/models/qwen2-1_5b-instruct-q4_k_m.gguf \
         https://huggingface.co/Qwen/Qwen2-1.5B-Instruct-GGUF/resolve/main/qwen2-1_5b-instruct-q4_k_m.gguf && \
    ls -lh /app/models/qwen2-1_5b-instruct-q4_k_m.gguf && \
    file /app/models/qwen2-1_5b-instruct-q4_k_m.gguf | grep -q "data" || (echo "Model file invalid" && exit 1)

# ---------- Expose port ----------
EXPOSE 8000

# ---------- Run FastAPI ----------
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
