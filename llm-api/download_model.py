import yaml
from pathlib import Path
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

def load_yaml_config(file_name: str) -> dict:
    """Load a YAML configuration file from the config directory."""
    path = Path(__file__).resolve().parent / "config" / file_name
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    print("Loading model configuration...")
    model_config = load_yaml_config("model_config.yaml")
    
    MODEL_ID = model_config["model"]["name"]
    print(f"Downloading model: {MODEL_ID}")
    
    # Configure quantization if enabled
    quant_config = None
    if model_config.get("quantization", {}).get("enabled", False):
        quant_config = BitsAndBytesConfig(
            load_in_4bit=(model_config["quantization"]["method"] == "4bit"),
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    
    # Download tokenizer
    print("Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    
    # Download model
    print("Downloading model...")
    if quant_config:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map="auto",
            quantization_config=quant_config,
            trust_remote_code=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map="auto",
            trust_remote_code=True
        )
    
    print("Model and tokenizer downloaded successfully!")

if __name__ == "__main__":
    main()