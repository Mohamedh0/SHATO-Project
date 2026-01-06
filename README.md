<div align="center">

# 🤖 SHATO — Smart Home Autonomous Task Operator

**An Intelligent Voice-Controlled Robotic Assistant**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

*Transform natural language into validated robot commands through an end-to-end voice pipeline*

[Getting Started](#-getting-started) • [Architecture](#-architecture) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**SHATO** (Smart Home Autonomous Task Operator) is a production-ready microservices platform that transforms an autonomous robot into an intelligent, voice-controlled assistant. The system implements a complete **Speech-to-Text → LLM → Text-to-Speech** pipeline with strict command validation to ensure safe and reliable robot operations.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice-to-Action Pipeline** | Seamless conversion from spoken commands to robot actions |
| 🛡️ **Strict Schema Validation** | Prevents hallucinated or unsafe commands from execution |
| 🏗️ **Microservices Architecture** | Scalable, maintainable, and independently deployable services |
| 📊 **Observability** | Built-in logging, metrics (Prometheus), and distributed tracing (OpenTelemetry) |
| 🔗 **Correlation Tracking** | End-to-end request tracing across all services |
| 🌐 **Web Interface** | Interactive Gradio-based UI for real-time voice interaction |

---

## 🏗️ Architecture

SHATO employs a **microservices architecture**, fully containerized and orchestrated via Docker Compose.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                         (Gradio Web App - :7860)                            │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ Audio Upload
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR SERVICE                               │
│                            (FastAPI - :8500)                                 │
│  • Routes requests between services    • Correlation ID propagation          │
│  • Structured logging (structlog)      • Prometheus metrics & OTLP tracing  │
└──────┬──────────────────┬──────────────────┬──────────────────┬─────────────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  STT Service │  │  LLM Service │  │  Validator   │  │  TTS Service │
│    :8002     │  │    :8000     │  │    :8001     │  │    :8003     │
├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
│ Whisper ASR  │  │ Llama.cpp    │  │ Pydantic     │  │ Coqui TTS    │
│ Audio → Text │  │ NL → Command │  │ Schema Valid │  │ Text → Audio │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### 🔧 Service Overview

| Service | Port | Technology | Responsibility |
|---------|------|------------|----------------|
| **UI Service** | `7860` | Gradio | Web interface for voice recording and playback |
| **Orchestrator** | `8500` | FastAPI, structlog | Pipeline coordination, logging, observability |
| **STT Service** | `8002` | FastAPI, Whisper | Speech-to-Text transcription |
| **LLM Service** | `8000` | FastAPI, Llama.cpp | Natural language to command mapping |
| **Validator** | `8001` | FastAPI, Pydantic | Command schema validation and execution |
| **TTS Service** | `8003` | FastAPI, Coqui TTS | Text-to-Speech synthesis |

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- [HuggingFace Account](https://huggingface.co/) (for model access token)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mohamedh0/SHATO-Project.git
   cd SHATO-Project
   ```

2. **Configure environment variables**
   ```bash
   # Create .env file from template
   cp .env.example .env
   
   # Add your HuggingFace token
   echo "HF_TOKEN=hf_your_token_here" >> .env
   ```

3. **Build and launch all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   
   Open your browser and navigate to: **http://localhost:7860**

### Quick Verification

```bash
# Check service health
curl http://localhost:8500/health      # Orchestrator
curl http://localhost:8000/health      # LLM Service
curl http://localhost:8001/health      # Validator
curl http://localhost:8002/health      # STT Service
curl http://localhost:8003/health      # TTS Service
```

---

## 📜 Robot Command Schema

All commands follow a strict JSON schema validated by Pydantic models to ensure safety and correctness.

### Command Structure

```json
{
  "command": "<command_name>",
  "command_params": { /* parameters */ },
  "verbal_response": "<natural language confirmation>"
}
```

### Available Commands

<details>
<summary><strong>🚗 move_to</strong> — Navigate to specific coordinates</summary>

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `x` | float | ✅ | -100 to 100 | X coordinate |
| `y` | float | ✅ | -100 to 100 | Y coordinate |

**Example:**
```json
{
  "command": "move_to",
  "command_params": { "x": 10.0, "y": -5.0 },
  "verbal_response": "On my way to that spot!"
}
```
</details>

<details>
<summary><strong>🔄 rotate</strong> — Rotate by specified angle</summary>

| Parameter | Type | Required | Options | Description |
|-----------|------|----------|---------|-------------|
| `angle` | float | ✅ | 0-360 | Rotation angle in degrees |
| `direction` | string | ✅ | `clockwise`, `counter-clockwise` | Rotation direction |

**Example:**
```json
{
  "command": "rotate",
  "command_params": { "angle": 90.0, "direction": "clockwise" },
  "verbal_response": "Spinning into position!"
}
```
</details>

<details>
<summary><strong>🛡️ start_patrol</strong> — Begin patrolling a predefined route</summary>

| Parameter | Type | Required | Options | Default | Description |
|-----------|------|----------|---------|---------|-------------|
| `route_id` | string | ✅ | `first_floor`, `bedrooms`, `second_floor` | — | Patrol route identifier |
| `speed` | string | ❌ | `slow`, `medium`, `fast` | `medium` | Movement speed |
| `repeat_count` | integer | ❌ | ≥1 or -1 (infinite) | 1 | Number of patrol cycles |

**Example:**
```json
{
  "command": "start_patrol",
  "command_params": { 
    "route_id": "first_floor", 
    "speed": "fast", 
    "repeat_count": 5 
  },
  "verbal_response": "Kicking off the patrol—let's roll!"
}
```
</details>

---

## 📡 API Reference

### Orchestrator Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/voice_flow` | Complete voice-to-action pipeline |
| `GET` | `/health` | Service health status |
| `GET` | `/metrics` | Prometheus metrics (when enabled) |

### Service-Specific Endpoints

| Service | Endpoint | Method | Description |
|---------|----------|--------|-------------|
| STT | `/transcribe` | `POST` | Audio file → Text |
| LLM | `/command` | `POST` | Text → Robot command |
| Validator | `/execute_command` | `POST` | Validate and execute command |
| TTS | `/speak` | `POST` | Text → Audio (base64) |

---

## 📁 Project Structure

```
SHATO-Project/
├── 📄 docker-compose.yml      # Container orchestration
├── 📄 README.md               # This file
├── 📁 orchestrator-api/       # Central orchestration service
│   ├── main.py                # FastAPI application
│   ├── config.py              # Configuration settings
│   └── requirements.txt       # Python dependencies
├── 📁 llm-api/                # LLM-based command generation
│   ├── api/                   # API endpoints and utilities
│   └── config/                # Prompt templates and model config
├── 📁 stt-api/                # Speech-to-Text service
│   └── api/                   # Whisper-based transcription
├── 📁 tts-api/                # Text-to-Speech service
│   └── api/                   # Coqui TTS integration
├── 📁 robot-validator-api/    # Command validation & execution
│   ├── api/                   # Pydantic schema validation
│   └── tests/                 # Unit tests
└── 📁 ui-service/             # Gradio web interface
    └── main.py                # UI application
```

---

## 🧪 Testing

```bash
# Run validator tests
cd robot-validator-api
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html
```

---

## 🛠️ Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies for a specific service
cd <service-directory>
pip install -r requirements.txt
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | HuggingFace API token | Required |
---
