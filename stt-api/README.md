# STT-Service

## Usage Instructions

### **Build the Docker image**

```bash
docker build -t myapp:latest .
```
---
### **Run the container**

```bash
docker run -p 8002:8002 -v $(pwd)/api:/app/api myapp:latest
```

---
### **Test the health endpoint in the browser**
```bash
http://localhost:8002
```
**Expected response**
```
{
  "message": "Server Is Running!"
}
```

###  **Request (Postman)**

- **Method:** POST  
- **URL:** `http://localhost:8002/transcribe`  
- **Body (form-data):**
  - Key: `audio`
  - Type: File
  - Value: Select a `.wav` file (e.g., `sample.wav`)