# Orchestrator-api

This project is an orchestrator API that acts as a central hub for a voice-activated robot. It integrates various microservices to translate a user's voice command into a validated, actionable instruction for a robot.

## 1. Features

* **Speech-to-Text (STT):** Transcribes user audio commands into text.
* **Large Language Model (LLM):** Processes transcribed text to infer a specific robot command and its parameters.
* **Command Validation:** Validates the inferred command against a predefined schema.
* **Text-to-Speech (TTS):** Converts a text response back into spoken audio.
* **Full Orchestration Flow:** A single endpoint (`/voice_flow`) handles the entire pipeline: STT → LLM → Validation → TTS.

***

## 2. Prerequisites

Before you begin, ensure you have the following installed:
* Python 3.11
* An Anaconda or Miniconda environment
* Git

***

## 3. Setup and Installation

1.  **Clone the Repository and Switch Branch:**
    ```bash
    git clone [https://github.com/Mohamedh0/SHATO-Project.git](https://github.com/Mohamedh0/SHATO-Project.git)
    cd SHATO-Project
    git checkout orchestrator-api
    ```
2.  **Create and Activate a Virtual Environment:**
    ```bash
    conda create --name orchestrator_env python=3.11
    conda activate orchestrator_env
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

***

## 4. Configuration

This project uses environment variables for configuration.
1.  Create a `.env` file in the project root by copying the `.env.example` file.
    ```bash
    cp .env.example .env
    ```
2.  Open the `.env` file and update the service URLs if they differ from the defaults.

***

## 5. Running the Application

To run the orchestrator service, use the following command:
```bash
uvicorn main:app --reload --port 8500
