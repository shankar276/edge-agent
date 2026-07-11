"""Test EdgeAgent inference."""
import sys
sys.path.insert(0, 'src')

from agent.inference import TransformersInferenceEngine

print("Loading model...")
engine = TransformersInferenceEngine('models/qwen2.5-0.5b-instruct')

print("\nGenerating response...")
response = engine.generate('What is AI?', max_new_tokens=100)
print(f"\nResponse: {response}")