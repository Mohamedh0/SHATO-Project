# robot-validator-api

## Usage Instructions

### **Build the Docker image**

```bash
docker build -t myapp:latest .
```
---
### **Run the container**

```bash
docker run -p 5000:5000 -v $(pwd)/api:/app/api myapp:latest
```
---
### **Test the health endpoint in the browser**
```bash
http://localhost:5000
```
**Expected response**
```
{
  "message": "Server Is Running!"
}
```