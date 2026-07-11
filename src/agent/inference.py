"""Transformers-based inference engine for EdgeAgent."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class TransformersInferenceEngine:
    """Transformers-based inference for Qwen models."""
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load model and tokenizer."""
        print(f"Loading model from {self.model_path}...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=False
        )
        
        # Load model (CPU only for now)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float32,  # Use float32 for CPU compatibility
            device_map="cpu",
            trust_remote_code=False
        )
        
        print(f"Model loaded successfully!")
        print(f"Device: {next(self.model.parameters()).device}")
    
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs."""
        return self.tokenizer.encode(text, return_tensors="pt")
    
    def decode(self, token_ids: List[int]) -> str:
        """Decode token IDs to text."""
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)
    
    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1
    ) -> str:
        """Generate text from prompt (non-streaming)."""
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature if temperature > 0 else 1.0,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=temperature > 0,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    def generate_stream(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1
    ) -> Generator[str, None, None]:
        """Generate text with streaming."""
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature if temperature > 0 else 1.0,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=temperature > 0,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
        for token_id in generated_ids:
            yield self.tokenizer.decode([token_id], skip_special_tokens=True)


def download_model(model_id: str, output_dir: str):
    """Download model from Hugging Face Hub."""
    from huggingface_hub import snapshot_download
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading {model_id}...")
    snapshot_download(
        repo_id=model_id,
        local_dir=output_path,
        local_dir_use_symlinks=False
    )
    print(f"Model downloaded to {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Download mode
        download_model(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "models/qwen2.5-0.5b-instruct")
    else:
        # Test mode - load existing model
        model_path = "models/qwen2.5-0.5b-instruct"
        engine = TransformersInferenceEngine(model_path)
        
        # Test generation
        response = engine.generate("Tell me about AI agents.", max_new_tokens=100)
        print("\nResponse:", response)