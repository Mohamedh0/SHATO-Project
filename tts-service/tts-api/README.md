# TTS Service - Enhanced Version

A robust Text-to-Speech service built with FastAPI and Coqui TTS, featuring comprehensive logging, correlation IDs, error handling, and OpenAPI documentation.

## Features

### Core Functionality
- **Text-to-Speech Conversion**: Convert text to speech using Coqui TTS models
- **Multiple Voice Support**: Support for different voices/speakers (model-dependent)
- **Speed Control**: Adjustable speech speed (0.5x to 2.0x)
- **Base64 Audio Output**: Returns audio as base64-encoded WAV data

### Enhanced Features
- **Structured Logging**: Comprehensive logging with correlation IDs
- **Request Tracking**: Correlation ID middleware for request tracing
- **Error Handling**: Robust error handling with detailed error responses
- **OpenAPI Documentation**: Complete API documentation with examples
- **Health Checks**: Multiple health check endpoints
- **CORS Support**: Cross-origin resource sharing enabled

## API Endpoints

### Health Endpoints

#### `GET /`
Basic health check endpoint.

**Response:**
```json
{
  "message": "TTS Service Running!",
  "status": "healthy",
  "model": "tts_models/en/ljspeech/tacotron2-DDC",
  "version": "1.0.0"
}
```

#### `GET /health`
Detailed health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "TTS Service",
  "model": "tts_models/en/ljspeech/tacotron2-DDC",
  "model_loaded": true,
  "version": "1.0.0",
  "timestamp": 1703123456.789
}
```

### TTS Endpoint

#### `POST /speak`
Convert text to speech.

**Request Body:**
```json
{
  "text": "Hello, Made In Alexandria! Welcome to our TTS service.",
  "voice": "female",
  "speed": 1.0
}
```

**Response:**
```json
{
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
  "model": "tts_models/en/ljspeech/tacotron2-DDC",
  "estimated_duration_sec": 2.5
}
```

**Parameters:**
- `text` (required): Text to convert to speech (1-1000 characters)
- `voice` (optional): Voice/speaker name if supported by the model
- `speed` (optional): Speech speed multiplier (0.5-2.0, default: 1.0)

## Error Handling

The service provides comprehensive error handling with detailed error responses:

### Error Response Format
```json
{
  "error": "Error Type",
  "detail": "Detailed error message",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Error Types
- **400 Bad Request**: Invalid input (empty text, invalid parameters)
- **422 Validation Error**: Request validation failed
- **500 Internal Server Error**: TTS generation failed
- **503 Service Unavailable**: TTS model not loaded

## Logging

### Log Format
```
2024-01-01 12:00:00,000 - __main__ - INFO - [123e4567-e89b-12d3-a456-426614174000] - Request started: POST /speak
```

### Log Levels
- **INFO**: Request/response logging, successful operations
- **WARNING**: Validation errors, non-critical issues
- **ERROR**: TTS generation failures, system errors
- **DEBUG**: Detailed parameter logging, cleanup operations

### Log Files
- Console output: Real-time logging
- File output: `tts_service.log` (persistent logging)

## Correlation IDs

Every request is assigned a unique correlation ID that:
- Is generated automatically if not provided
- Can be provided via `X-Correlation-ID` header
- Flows through all logs and responses
- Enables request tracing across the system

## Installation & Setup

### Prerequisites
- Python 3.11+
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SHATO-Project/tts-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the service**
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 7000 --reload
   ```

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t tts-service .
   ```

2. **Run the container**
   ```bash
   docker run -p 7000:7000 tts-service
   ```

## API Documentation

Once the service is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:7000/docs
- **ReDoc**: http://localhost:7000/redoc

## Usage Examples

### Basic Text-to-Speech
```bash
curl -X POST "http://localhost:7000/speak" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, Made In Alexandria!"
  }'
```

### With Custom Parameters
```bash
curl -X POST "http://localhost:7000/speak" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: my-custom-id" \
  -d '{
    "text": "Welcome to our TTS service!",
    "voice": "female",
    "speed": 1.2
  }'
```

### Health Check
```bash
curl -X GET "http://localhost:7000/health"
```

## Configuration

### Environment Variables
- `PYTHONUNBUFFERED=1`: Ensures immediate log output
- `PYTHONPATH=/app`: Sets Python path for imports

### Model Configuration
The service uses the `tts_models/en/ljspeech/tacotron2-DDC` model by default. This can be modified in `api/main.py`:

```python
MODEL_NAME = "tts_models/en/ljspeech/tacotron2-DDC"
```

## Monitoring & Troubleshooting

### Log Analysis
Monitor the service using the structured logs:

```bash
# Follow logs in real-time
tail -f tts_service.log

# Filter by correlation ID
grep "123e4567-e89b-12d3-a456-426614174000" tts_service.log

# Check for errors
grep "ERROR" tts_service.log
```

### Common Issues

1. **Model Loading Failures**
   - Check internet connection for model download
   - Verify sufficient disk space
   - Check logs for specific error messages

2. **Audio Generation Failures**
   - Verify text input is valid
   - Check model compatibility with voice parameters
   - Monitor system resources (CPU/Memory)

3. **High Memory Usage**
   - TTS models are memory-intensive
   - Consider using smaller models for production
   - Monitor container memory limits

## Development

### Project Structure
```
tts-api/
├── api/
│   ├── main.py          # Main FastAPI application
│   └── schema.py        # Pydantic models and validation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
└── README.md           # This documentation
```

### Adding New Features
1. Update `schema.py` for new request/response models
2. Add new endpoints in `main.py`
3. Update error handling as needed
4. Add comprehensive logging
5. Update this README

## License

This project is part of the Made In Alexandria training program.

## Support

For issues and questions, please refer to the project documentation or contact the development team.