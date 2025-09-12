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

---
### **Run tests locally**

1) Create and activate a virtualenv (recommended)
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```
2) Install dependencies
```bash
pip install -r requirements.txt -r dev-requirements.txt
```
3) Run tests with coverage
```bash
pytest -q --maxfail=1 --disable-warnings --cov=api --cov-report=term-missing
```
4) Run a specific test file
```bash
pytest api/tests/test_validator.py -q
```