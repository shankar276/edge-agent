"""Download Qwen model for EdgeAgent."""
from huggingface_hub import snapshot_download

model_id = "Qwen/Qwen2.5-0.5B-Instruct"
output_dir = "models/qwen2.5-0.5b-instruct"

print(f"Downloading {model_id}...")
snapshot_download(
    repo_id=model_id,
    local_dir=output_dir,
    local_dir_use_symlinks=False
)
print(f"Model downloaded to {output_dir}")