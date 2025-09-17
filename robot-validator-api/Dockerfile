# Python Image
FROM python:3.11-slim

# Working Directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY api/ ./api/

# Expose port
EXPOSE 8001

# Run the application (main.py is inside /app/api/)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
