# ---------- Base Image ----------
FROM python:3.11-slim

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Copy requirements first (leverage caching) ----------
COPY requirements.txt .

# ---------- Install dependencies ----------
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------- Copy app code ----------
COPY . .

# ---------- Expose port ----------
EXPOSE 8500

# ---------- Run FastAPI with Uvicorn ----------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8500"]
