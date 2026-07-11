"""Tool implementations for EdgeAgent."""
import os
import re
import subprocess
import psutil
import platform
from pathlib import Path
from typing import Dict, Any, List


def read_file(path: str) -> Dict[str, Any]:
    """Read contents of a local file (restricted to ./data/ directory)."""
    try:
        p = Path(path).resolve()
        
        # Restrict to ./data/ directory only
        data_dir = Path("./data/").resolve()
        if not str(p).startswith(str(data_dir)):
            return {"error": f"Access denied: Path must be within {data_dir}"}
        
        if not p.exists():
            return {"error": f"File not found: {path}"}
        if not p.is_file():
            return {"error": f"Not a file: {path}"}
        
        content = p.read_text(encoding="utf-8")
        return {"content": content, "path": str(p), "size": len(content)}
    except Exception as e:
        return {"error": str(e)}


def write_file(path: str, content: str) -> Dict[str, Any]:
    """Write content to a local file (restricted to ./output/ directory)."""
    try:
        p = Path(path).resolve()
        
        # Restrict to ./output/ directory only
        output_dir = Path("./output/").resolve()
        if not str(p).startswith(str(output_dir)):
            return {"error": f"Access denied: Path must be within {output_dir}"}
        
        # Block dangerous file extensions
        dangerous_extensions = [".sh", ".py", ".bashrc", ".bash_profile", ".zshrc"]
        if any(p.suffix.lower() == ext for ext in dangerous_extensions):
            return {"error": f"Blocked file extension: {p.suffix}"}
        
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"success": True, "path": str(p), "size": len(content)}
    except Exception as e:
        return {"error": str(e)}


def list_files(path: str) -> Dict[str, Any]:
    """List files in a directory."""
    try:
        p = Path(path).resolve()
        if not p.exists():
            return {"error": f"Directory not found: {path}"}
        if not p.is_dir():
            return {"error": f"Not a directory: {path}"}
        
        files = []
        for item in p.iterdir():
            files.append({
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            })
        return {"files": files, "path": str(p)}
    except Exception as e:
        return {"error": str(e)}


def run_command(command: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute a shell command (restricted to whitelisted commands)."""
    try:
        # Block dangerous characters
        dangerous_chars = [";", "|", "&", "$", "`", ">", "<", "\n"]
        if any(char in command for char in dangerous_chars):
            return {"error": "Command contains blocked characters"}
        
        # Whitelist of allowed commands (base command only, no args)
        allowed_commands = ["ls", "cat", "echo", "pwd", "date", "whoami"]
        cmd_parts = command.split()
        base_cmd = cmd_parts[0] if cmd_parts else ""
        
        if base_cmd not in allowed_commands:
            return {"error": f"Command not allowed: {base_cmd}"}
        
        # Disable shell=True for security
        result = subprocess.run(
            cmd_parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"error": str(e)}


def get_system_info() -> Dict[str, Any]:
    """Get system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu": {
                "count": psutil.cpu_count(),
                "percent": cpu_percent
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": round((disk.used / disk.total) * 100, 1)
            }
        }
    except Exception as e:
        return {"error": str(e)}


# Tool registry
TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "run_command": run_command,
    "get_system_info": get_system_info,
}


def get_tool(name: str):
    """Get tool function by name."""
    return TOOLS.get(name)


def list_tools() -> List[Dict[str, Any]]:
    """List all available tools."""
    return [
        {"name": "read_file", "description": "Read contents of a local file"},
        {"name": "write_file", "description": "Write content to a local file"},
        {"name": "list_files", "description": "List files in a directory"},
        {"name": "run_command", "description": "Execute a shell command"},
        {"name": "get_system_info", "description": "Get system resource usage"},
    ]


if __name__ == "__main__":
    # Test tools
    print(get_system_info())