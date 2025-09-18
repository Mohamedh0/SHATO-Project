# Project SHATO – Voice-Controlled Robotic Assistant  

## 📌 Overview  
Project SHATO aims to transform an autonomous robot into an **intelligent, voice-controlled assistant**.  
The system builds a **Speech-to-Text → LLM → Text-to-Speech pipeline**, ensuring every generated command is **validated against a strict schema** before being executed by the simulated robot control system.  

Key Features:  
- End-to-end voice-to-action pipeline.  
- Strict validation to prevent hallucinated or unsafe commands.  
- Modular **microservices architecture** with containerization.  
- Live interaction via **Gradio/Streamlit web interface**.  

---

## 🏗️ System Architecture  

The project uses a **microservices architecture**, containerized and orchestrated via Docker Compose.  

### Services  
1. **Orchestrator Service (`orchestrator-api`)**  
   - Framework: FastAPI  
   - Routes data between services and ensures validation.  

2. **Speech-to-Text Service (`stt-service`)**  
   - Framework: FastAPI, TorchServe (or similar)  
   - Model: Whisper-Base (or another deep learning STT model).  

3. **LLM Brain Service (`llm-service`)**  
   - Framework: FastAPI, Llama_cpp 
   - Maps natural language → valid robot commands.  
   - Outputs: JSON command + verbal response.  

4. **Text-to-Speech Service (`tts-service`)**  
   - Framework: FastAPI, TTS 
   - Model: Any deep learning TTS model.  

5. **User Interface (`ui-service`)**  
   - Framework: Gradio  
   - Provides a web interface with a “Record” button.  

6. **Robot Validator & Control Service (`robot-validator-api`)**  
   - Framework: FastAPI 
   - Validates commands against schema.  
   - Logs success/error messages.  

---

## 📜 Strict Robot Command Schema  

Every command must follow the format:  

```json
{
  "command": "<command_name>",
  "command_params": { ... },
  "verbal_response":"LLM generate that",
}
```

### Allowed Commands  

#### 1. `move_to`  
- **Parameters:**  
  - `x` (float, required)  
  - `y` (float, required)  

```json
{
  "command": "move_to",
  "command_params": { "x": 10, "y": -5 },
}
```

#### 2. `rotate`  
- **Parameters:**  
  - `angle` (float, required)  
  - `direction` ("clockwise" | "counter-clockwise")  

```json
{
  "command": "rotate",
  "command_params": { "angle": 90, "direction": "clockwise" }
}
```

#### 3. `start_patrol`  
- **Parameters:**  
  - `route_id` (string, required; one of ["first_floor", "bedrooms", "second_floor"])  
  - `speed` ("slow" | "medium" | "fast", optional; default = "medium")  
  - `repeat_count` (integer ≥1 or -1 for continuous; optional; default = 1)  

```json
{
  "command": "start_patrol",
  "command_params": { "route_id": "first_floor", "speed": "fast", "repeat_count": 5 }
}
```

---

## ⚙️ Installation & Setup  

### Prerequisites  
- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/install/)  

### Steps  
1. Clone this repository:  
   ```bash
   git clone https://github.com/Mohamedh0/SHATO-Project.git
   cd SHATO-Project
   ```

2. Make the .env.example to .env and get the HuggingFace Token
   - `HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx`

3. Build and run all services:  
   ```bash
   docker-compose up --build
   ```

4. Access the UI:  
   - Open browser at: `http://localhost:7860`  

---

## ✅ Definition of Done  

The project is complete when:  
- All six services run with a single `docker-compose up`.  
- UI allows live voice interaction.  
- Valid commands are accepted and logged by `robot-validator-api`.  
- Invalid commands are rejected and logged properly.  
- Project hosted on GitHub with PR-based workflow.  
- This README provides full setup/run instructions.  

---
