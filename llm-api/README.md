# LLM API Service

A FastAPI service for converting natural language instructions into robot commands using Large Language Models.

## LLM Integration

The `/infer` endpoint converts natural language instructions into validated robot commands.

### How it works
1. Input prompt is sent as JSON to `POST /infer`.
2. The model generates output based on configuration in `config/model_config.yaml`.
3. The output is parsed and validated against strict schemas in `api/schema.py`.
4. If valid, a structured command is returned; otherwise, an error response is given.

### Example request
```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Move the robot to coordinates (5, -2)"}'



## Quick Start

### Using Docker

```bash
# Build the image
docker build -t llm-api .

# Run the container
docker run -p 8000:8000 llm-api
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Model Configuration

The service uses `config/model_config.yaml` to control model selection and behavior.

### Available Models

1. **microsoft/DialoGPT-medium** (default)
   - Balanced performance and accuracy
   - Good for most use cases
   - Memory usage: ~1.5GB

2. **gpt2**
   - Smaller, faster model
   - Good for development/testing
   - Memory usage: ~0.5GB

3. **microsoft/DialoGPT-large**
   - Higher accuracy
   - More resource intensive
   - Memory usage: ~3GB

### Changing Models

Edit `config/model_config.yaml`:

```yaml
model:
  name: "gpt2"  # Change this line
  type: "causal_lm"
  max_length: 256
  temperature: 0.7
```

Then rebuild the Docker image:

```bash
docker build -t llm-api .
```

### Memory Optimization

For memory-constrained environments, enable quantization:

```yaml
quantization:
  enabled: true  # Set to true
  method: "4bit"
```

This reduces memory usage by ~75% but may slightly impact accuracy.

## API Endpoints

- `GET /health` - Health check
- `POST /infer` - Convert natural language to robot commands

## Environment Variables

- `MODEL_NAME` - Override model selection (e.g., `gpt2`)
- `QUANTIZATION_ENABLED` - Enable quantization (`true`/`false`)

Example:
```bash
docker run -p 8000:8000 -e MODEL_NAME=gpt2 llm-api
```
