"""Model download, quantization, and ONNX conversion script."""
import os
import sys
import argparse
from pathlib import Path

# Try importing required libraries
try:
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer, AutoConfig
    import torch
    from optimum.onnxruntime import ORTModelForCausalLM
except ImportError as e:
    print(f"Missing dependencies. Install with:")
    print("pip install huggingface_hub transformers torch optimum[onnxruntime]")
    sys.exit(1)


def download_model(model_id: str, output_dir: Path, token: str = None):
    """Download model from Hugging Face Hub."""
    print(f"Downloading {model_id}...")
    snapshot_download(
        repo_id=model_id,
        local_dir=output_dir,
        token=token,
        local_dir_use_symlinks=False,
        trust_repo=False
    )
    print(f"Downloaded to {output_dir}")


def convert_to_onnx(model_dir: Path, output_dir: Path, quantize: bool = True):
    """Convert PyTorch model to ONNX format with optional quantization."""
    print(f"Converting to ONNX...")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=False)
    tokenizer.save_pretrained(output_dir)
    
    # Load model config
    config = AutoConfig.from_pretrained(model_dir, trust_remote_code=False)
    
    # Export to ONNX
    ort_model = ORTModelForCausalLM.from_pretrained(
        model_dir,
        export=True,
        trust_remote_code=False,
        use_cache=True,
        use_io_binding=True
    )
    
    if quantize:
        print("Applying dynamic quantization (INT8)...")
        from optimum.onnxruntime import ORTQuantizer
        from optimum.onnxruntime.configuration import AutoQuantizationConfig
        
        quantizer = ORTQuantizer.from_pretrained(ort_model)
        qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)
        quantizer.quantize(save_dir=output_dir, quantization_config=qconfig)
    else:
        ort_model.save_pretrained(output_dir)
    
    print(f"ONNX model saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Download and convert Qwen model for edge deployment")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct", help="HF model ID")
    parser.add_argument("--output", default="models/qwen2.5-0.5b-instruct-onnx", help="Output directory")
    parser.add_argument("--no-quantize", action="store_true", help="Skip INT8 quantization")
    parser.add_argument("--token", help="HF token for gated models")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    model_dir = output_dir / "model"
    
    if not (model_dir / "config.json").exists():
        download_model(args.model, model_dir, args.token)
    else:
        print(f"Model already exists at {model_dir}")
    
    # Convert to ONNX
    onnx_dir = output_dir
    convert_to_onnx(model_dir, onnx_dir, quantize=not args.no_quantize)
    
    print("\nDone! Model ready for edge deployment.")
    print(f"Path: {onnx_dir}")


if __name__ == "__main__":
    main()