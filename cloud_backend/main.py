"""EdgeAgent Cloud Backend - Lightweight API for model management and telemetry."""
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import json
import os
import sqlite3
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

app = FastAPI(title="EdgeAgent Cloud Backend", version="1.0.0")

# SQLite database for telemetry
DATABASE_PATH = os.getenv("EDGE_AGENT_DB_PATH", "telemetry.db")

# Model registry
model_registry = {
    "current_version": "qwen2.5-0.5b-instruct",
    "latest_version": "qwen2.5-0.5b-instruct",
    "download_url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct"
}

# API key for authentication (set via environment variable)
API_KEY = os.getenv("EDGE_AGENT_API_KEY", "")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            cpu_usage REAL NOT NULL,
            memory_usage REAL NOT NULL,
            inference_latency_ms REAL NOT NULL,
            tool_calls INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Rate limiter setup
@app.on_event("startup")
async def startup():
    init_db()
    redis_connection = redis.from_url("redis://localhost")
    await FastAPILimiter.init(redis_connection)

# Dependency for API key authentication
async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

class TelemetryEntry(BaseModel):
    agent_id: str
    timestamp: str
    cpu_usage: float
    memory_usage: float
    inference_latency_ms: float
    tool_calls: int

class ModelCheckRequest(BaseModel):
    current_version: str

@app.get("/")
def root():
    return {"message": "EdgeAgent Cloud Backend is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/model/check")
async def check_model_update(
    request: ModelCheckRequest,
    api_key: str = Depends(verify_api_key)
):
    """Check if a newer model version is available."""
    update_available = request.current_version != model_registry["latest_version"]
    return {
        "update_available": update_available,
        "current_version": request.current_version,
        "latest_version": model_registry["latest_version"],
        "download_url": model_registry["download_url"] if update_available else None
    }

@app.post("/api/telemetry")
@RateLimiter(times=10, seconds=60)
async def log_telemetry(
    request: Request,
    entry: TelemetryEntry,
    api_key: str = Depends(verify_api_key)
):
    """Log telemetry data from EdgeAgent instances."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO telemetry (agent_id, timestamp, cpu_usage, memory_usage, inference_latency_ms, tool_calls)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        entry.agent_id,
        entry.timestamp,
        entry.cpu_usage,
        entry.memory_usage,
        entry.inference_latency_ms,
        entry.tool_calls
    ))
    conn.commit()
    
    # Get total entries
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    total_entries = cursor.fetchone()[0]
    conn.close()
    
    return {"status": "logged", "total_entries": total_entries}

@app.get("/api/telemetry/stats")
@RateLimiter(times=10, seconds=60)
async def get_telemetry_stats(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Get aggregated telemetry statistics."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    total_entries = cursor.fetchone()[0]
    
    if total_entries == 0:
        conn.close()
        return {"message": "No telemetry data yet", "stats": {}}
    
    cursor.execute("SELECT cpu_usage, memory_usage, inference_latency_ms, tool_calls FROM telemetry")
    rows = cursor.fetchall()
    conn.close()
    
    cpu_usages = [row[0] for row in rows]
    memory_usages = [row[1] for row in rows]
    latencies = [row[2] for row in rows]
    tool_calls = [row[3] for row in rows]
    
    return {
        "total_entries": total_entries,
        "stats": {
            "avg_cpu_usage": sum(cpu_usages) / len(cpu_usages),
            "avg_memory_usage": sum(memory_usages) / len(memory_usages),
            "avg_inference_latency_ms": sum(latencies) / len(latencies),
            "total_tool_calls": sum(tool_calls)
        }
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Simple web dashboard for monitoring."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EdgeAgent Cloud Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            .status {{ padding: 10px; background: #d4edda; border-left: 4px solid #28a745; margin: 20px 0; }}
            .stat {{ margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 4px; }}
            .stat-label {{ font-weight: bold; color: #555; }}
            .stat-value {{ font-size: 24px; color: #007bff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 EdgeAgent Cloud Dashboard</h1>
            <div class="status">
                <strong>Status:</strong> ✅ Operational
            </div>
            <div class="stat">
                <div class="stat-label">Current Model Version</div>
                <div class="stat-value">{model_registry['current_version']}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Telemetry Entries</div>
                <div class="stat-value">{get_telemetry_count()}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Server Time</div>
                <div class="stat-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            <p style="margin-top: 30px; color: #666;">
                <strong>API Endpoints:</strong><br>
                • GET /health - Health check<br>
                • POST /api/model/check - Check for model updates<br>
                • POST /api/telemetry - Log telemetry data<br>
                • GET /api/telemetry/stats - Get telemetry statistics
            </p>
        </div>
    </body>
    </html>
    """
    return html_content

def get_telemetry_count():
    """Helper function to get telemetry count for dashboard."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
