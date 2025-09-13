# LLM API Service

A FastAPI service for converting natural language instructions into robot commands using Large Language Models.

### Create LLM FastAPI Service

- Implemented the initial FastAPI application with `/health` and `/infer` endpoints.
- `/health` returns a simple health check message to confirm the service is running.
- `/infer` currently returns a **dummy robot command** (`move_to`) but passes through the **LLM validator** to ensure the output complies with the schema.
- This setup makes the service fully testable and ready for integration with the real LLM model in later tasks.


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
