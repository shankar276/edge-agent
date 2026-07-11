"""Main EdgeAgent loop with tool calling support."""
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass, field

from agent.inference import TransformersInferenceEngine
from tools import get_tool, list_tools


@dataclass
class Message:
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


class EdgeAgent:
    """On-device AI agent with tool calling capabilities."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.engine = None
        self.messages: List[Message] = []
        self._init_engine()
        self._init_system_prompt()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML."""
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f)
        return {}
    
    def _init_engine(self):
        """Initialize inference engine."""
        model_config = self.config.get("model", {})
        model_path = model_config.get("path", "models/qwen2.5-0.5b-instruct")
        self.engine = TransformersInferenceEngine(model_path)
    
    def _init_system_prompt(self):
        """Initialize system prompt and tools."""
        system_prompt = self.config.get("agent", {}).get("system_prompt", "")
        tools_config = self.config.get("agent", {}).get("tools", [])
        
        # Build tool descriptions for the model
        tool_descriptions = []
        for tool in tools_config:
            tool_descriptions.append({
                "type": "function",
                "function": tool
            })
        
        # Create system message with tool definitions
        tools_json = json.dumps(tool_descriptions, indent=2)
        full_system_prompt = f"""{system_prompt}

Available tools:
{tools_json}

When you need to use a tool, respond with a JSON object in this format:
{{
  "tool_calls": [
    {{
      "id": "call_123",
      "type": "function",
      "function": {{
        "name": "tool_name",
        "arguments": "{{\"arg\": \"value\"}}"
      }}
    }}
  ]
}}

Only use tools when necessary. If no tool is needed, respond normally."""
        
        self.messages = [Message(role="system", content=full_system_prompt)]
    
    def _extract_tool_calls(self, text: str) -> List[Dict]:
        """Extract tool calls from model response."""
        tool_calls = []
        try:
            data = json.loads(text) # Try to parse the entire response as JSON
            raw_calls = data.get("tool_calls", [])
            print(f"[DEBUG] Raw calls from full response: {raw_calls}")
            for tc in raw_calls:
                name = tc.get("name") or tc.get("id") or tc.get("function", {}).get("name", "")
                args = tc.get("arguments", tc.get("function", {}).get("arguments", {}))
                if isinstance(args, dict):
                    args = json.dumps(args)
                tool_calls.append({
                    "id": tc.get("id", "call_1"),
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": args
                    }
                })
        except json.JSONDecodeError:
            print("[DEBUG] Full response is not valid JSON.")
        except Exception as e:
            print(f"[DEBUG] Extraction error: {e}")
        return tool_calls
    
    def _execute_tool(self, tool_call: Dict) -> Dict:
        """Execute a tool call and return result."""
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments_str = function.get("arguments", "{}")
        
        try:
            arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
        except (json.JSONDecodeError, TypeError):
            arguments = {}
        
        tool_func = get_tool(name)
        if not tool_func:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            result = tool_func(**arguments)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def chat(self, user_input: str, stream: bool = False) -> Generator[str, None, str]:
        """Chat with the agent."""
        # Add user message
        self.messages.append(Message(role="user", content=user_input))
        
        # Build prompt
        prompt = self._build_prompt()
        
        # Generation config
        gen_config = self.config.get("model", {})
        max_new_tokens = gen_config.get("max_new_tokens", 512)
        temperature = gen_config.get("temperature", 0.7)
        top_p = gen_config.get("top_p", 0.9)
        top_k = gen_config.get("top_k", 50)
        repetition_penalty = gen_config.get("repetition_penalty", 1.1)
        
        # Generate response
        full_response = ""
        if stream:
            for chunk in self.engine.generate_stream(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty
            ):
                full_response += chunk
                yield chunk
        else:
            full_response = self.engine.generate(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty
            )
        
        # Check for tool calls
        tool_calls = self._extract_tool_calls(full_response)
        print(f"\n[DEBUG] Extracted tool calls: {tool_calls}")
        
        if tool_calls:
            # Execute tools
            tool_results = []
            for tc in tool_calls:
                result = self._execute_tool(tc)
                print(f"[DEBUG] Tool result: {result}")
                tool_results.append({
                    "tool_call_id": tc.get("id"),
                    "result": result
                })
            
            # Add tool results to messages
            for tr in tool_results:
                self.messages.append(Message(
                    role="tool",
                    content=json.dumps(tr["result"]),
                    tool_call_id=tr["tool_call_id"]
                ))
            
            # Generate final response after tool execution
            prompt = self._build_prompt()
            final_response = self.engine.generate(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty
            )
            
            full_response = final_response
            if stream:
                yield final_response
        
        # Add assistant response to history
        self.messages.append(Message(role="assistant", content=full_response))
        
        return full_response
    
    def _build_prompt(self) -> str:
        """Build chat prompt from messages."""
        # Simple chat template for Qwen
        prompt = ""
        for msg in self.messages:
            if msg.role == "system":
                prompt += f"<|im_start|>system\n{msg.content}<|im_end|>\n"
            elif msg.role == "user":
                prompt += f"<|im_start|>user\n{msg.content}<|im_end|>\n"
            elif msg.role == "assistant":
                prompt += f"<|im_start|>assistant\n{msg.content}<|im_end|>\n"
            elif msg.role == "tool":
                prompt += f"<|im_start|>tool\n{msg.content}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"
        return prompt
    
    def reset(self):
        """Reset conversation history."""
        self._init_system_prompt()


def main():
    """CLI entry point."""
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    
    print("Initializing EdgeAgent...")
    agent = EdgeAgent(config_path)
    print("Ready! Type 'exit' to quit, 'reset' to clear history.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ("exit", "quit"):
                break
            if user_input.lower() == "reset":
                agent.reset()
                print("History cleared.\n")
                continue
            
            print("Agent: ", end="", flush=True)
            for chunk in agent.chat(user_input, stream=True):
                print(chunk, end="", flush=True)
            print("\n")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nGoodbye!")


if __name__ == "__main__":
    main()