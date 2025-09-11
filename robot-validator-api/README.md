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
## Example Commands

### 1. move_to
```json
{
  "command": "move_to",
  "command_params": { "x": 10, "y": -5 }
}
```

### 2. rotate
```json
{
  "command": "rotate",
  "command_params": { "angle": 90.0, "direction": "clockwise" }
}
```

### 3. start_patrol
```json
{
  "command": "start_patrol",
  "command_params": { "route_id": "first_floor", "speed": "fast", "repeat_count": 3 }
}
```