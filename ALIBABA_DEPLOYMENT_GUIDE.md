# 🚀 Alibaba Cloud Deployment Guide for EdgeAgent

## Overview

This guide walks you through deploying the **EdgeAgent Cloud Backend** on Alibaba Cloud Simple Application Server (SAS). The backend provides:
- Model registry API (check for updates)
- Telemetry logging (track agent performance)
- Health check endpoint
- Web-based status dashboard

---

## 📋 Prerequisites

- Alibaba Cloud account with $40 coupon (ID: 501018800150172)
- Local EdgeAgent project completed and tested
- SSH client (PuTTY for Windows, or built-in SSH)

---

## Step 1: Create Simple Application Server (SAS)

### 1.1 Navigate to SAS Console
1. Log in to [Alibaba Cloud Console](https://www.alibabacloud.com)
2. Search for "Simple Application Server" in the search bar
3. Click on **Simple Application Server**

### 1.2 Create Server Instance
1. Click **Create Server**
2. Select **Region**: Choose closest to you (e.g., Singapore, Mumbai, US-West)
3. Select **Image Type**: Application Image
4. Select **Image**: **Docker v26.1.3** (pre-installed Docker)
5. Select **Plan**: Choose cheapest option (1 vCPU, 1-2GB RAM, 40GB storage)
6. **Instance Name**: `edge-agent-server`
7. **Subscription Duration**: 1 month
8. Click **Buy Now** and complete payment (coupon will be applied)

### 1.3 Note Your Server Details
After creation, note down:
- **Public IP Address**: `xxx.xxx.xxx.xxx` (auto-assigned)
- **Instance ID**: For reference

### 1.4 Reset Root Password
1. Go to your instance dashboard
2. Click **Reset Password**
3. Set a strong password (e.g., `EdgeAgent2026!Secure`)
4. **Important**: Restart the server after password reset

---

## Step 2: Configure Firewall Rules

### 2.1 Access Firewall Settings
1. Go to your SAS instance
2. Click **Firewall** tab
3. Click **Add Rule**

### 2.2 Add Required Ports
Add these rules:

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Your IP only | SSH access |
| 8080 | TCP | 0.0.0.0/0 | EdgeAgent API |
| 80 | TCP | 0.0.0.0/0 | Web dashboard (optional) |

**Security Note**: Restrict SSH (port 22) to your IP address only.

---

## Step 3: Connect to Your Server

### 3.1 Using SSH (Recommended)
Open PowerShell or Command Prompt:

```bash
ssh root@YOUR_SERVER_IP
```

Enter the password you set in Step 1.4.

### 3.2 Using Alibaba Cloud Workbench (Alternative)
1. Go to your SAS instance dashboard
2. Click **Connect** button
3. Select **Workbench** (browser-based SSH)
4. Log in as `root` with your password

---

## Step 4: Prepare Server Environment

### 4.1 Verify Docker Installation
```bash
docker --version
docker compose version
```

Expected output:
```
Docker version 26.1.3
Docker Compose version v2.x.x
```

### 4.2 Update System
```bash
apt update && apt upgrade -y
```

### 4.3 Create Project Directory
```bash
mkdir -p /opt/edge-agent-cloud
cd /opt/edge-agent-cloud
```

---

## Step 5: Deploy EdgeAgent Cloud Backend

### 5.1 Create Backend Files Locally

On your **local machine**, create these files in `C:\Savio\My_QWEN_Project\edge-agent\cloud_backend\`:

#### File 1: `main.py` (FastAPI Backend)
```python
"""EdgeAgent Cloud Backend - Lightweight API for model management and telemetry."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import json
import os

app = FastAPI(title="EdgeAgent Cloud Backend", version="1.0.0")

# In-memory storage (use Redis/PostgreSQL in production)
telemetry_logs = []
model_registry = {
    "current_version": "qwen2.5-0.5b-instruct",
    "latest_version": "qwen2.5-0.5b-instruct",
    "download_url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct"
}

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
def check_model_update(request: ModelCheckRequest):
    """Check if a newer model version is available."""
    update_available = request.current_version != model_registry["latest_version"]
    return {
        "update_available": update_available,
        "current_version": request.current_version,
        "latest_version": model_registry["latest_version"],
        "download_url": model_registry["download_url"] if update_available else None
    }

@app.post("/api/telemetry")
def log_telemetry(entry: TelemetryEntry):
    """Log telemetry data from EdgeAgent instances."""
    telemetry_logs.append(entry.dict())
    # Keep only last 1000 entries
    if len(telemetry_logs) > 1000:
        telemetry_logs.pop(0)
    return {"status": "logged", "total_entries": len(telemetry_logs)}

@app.get("/api/telemetry/stats")
def get_telemetry_stats():
    """Get aggregated telemetry statistics."""
    if not telemetry_logs:
        return {"message": "No telemetry data yet", "stats": {}}
    
    cpu_usages = [e["cpu_usage"] for e in telemetry_logs]
    memory_usages = [e["memory_usage"] for e in telemetry_logs]
    latencies = [e["inference_latency_ms"] for e in telemetry_logs]
    
    return {
        "total_entries": len(telemetry_logs),
        "stats": {
            "avg_cpu_usage": sum(cpu_usages) / len(cpu_usages),
            "avg_memory_usage": sum(memory_usages) / len(memory_usages),
            "avg_inference_latency_ms": sum(latencies) / len(latencies),
            "total_tool_calls": sum(e["tool_calls"] for e in telemetry_logs)
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
                <div class="stat-value">{len(telemetry_logs)}</div>
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

#### File 2: `requirements.txt`
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
pydantic==2.7.4
```

#### File 3: `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### File 4: `docker-compose.yml`
```yaml
version: '3.8'

services:
  edge-agent-cloud:
    build: .
    ports:
      - "8080:8080"
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped
    volumes:
      - ./data:/app/data
```

### 5.2 Transfer Files to Server

**Option A: Using SCP (Recommended)**
From your local PowerShell:
```powershell
scp -r C:\Savio\My_QWEN_Project\edge-agent\cloud_backend\* root@YOUR_SERVER_IP:/opt/edge-agent-cloud/
```

**Option B: Using SFTP Client (FileZilla/WinSCP)**
1. Connect to your server IP with root credentials
2. Navigate to `/opt/edge-agent-cloud/`
3. Upload all files from `cloud_backend/` folder

### 5.3 Build and Deploy on Server

SSH into your server and run:
```bash
cd /opt/edge-agent-cloud

# Create data directory
mkdir -p data

# Build Docker image
docker compose build

# Start the service
docker compose up -d

# Check status
docker compose ps
docker compose logs -f edge-agent-cloud
```

---

## Step 6: Test Your Deployment

### 6.1 Test Health Endpoint
```bash
curl http://YOUR_SERVER_IP:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-07-04T12:00:00",
  "version": "1.0.0"
}
```

### 6.2 Test Model Check API
```bash
curl -X POST http://YOUR_SERVER_IP:8080/api/model/check \
  -H "Content-Type: application/json" \
  -d '{"current_version": "qwen2.5-0.5b-instruct"}'
```

### 6.3 Access Web Dashboard
Open your browser and navigate to:
```
http://YOUR_SERVER_IP:8080/dashboard
```

You should see the EdgeAgent Cloud Dashboard with status information.

### 6.4 Test Telemetry Logging
```bash
curl -X POST http://YOUR_SERVER_IP:8080/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "local-agent-001",
    "timestamp": "2026-07-04T12:00:00",
    "cpu_usage": 45.2,
    "memory_usage": 78.5,
    "inference_latency_ms": 1250.5,
    "tool_calls": 3
  }'
```

---

## Step 7: Capture Screenshots for Hackathon Submission

### 7.1 Required Screenshots

Take screenshots of:

1. **Alibaba Cloud Console**: Show your SAS instance with Public IP
2. **SSH Terminal**: Show successful connection to server
3. **Docker Status**: Run `docker compose ps` showing running container
4. **Health Check**: Browser showing `http://YOUR_SERVER_IP:8080/health` response
5. **Web Dashboard**: Browser showing `http://YOUR_SERVER_IP:8080/dashboard`
6. **API Test**: Terminal showing successful `curl` commands

### 7.2 Save Screenshots
Save all screenshots in:
```
C:\Savio\My_QWEN_Project\edge-agent\docs\alibaba-cloud-screenshots\
```

---

## Step 8: Integrate with Local EdgeAgent (Optional)

To make your local EdgeAgent communicate with the cloud backend:

### 8.1 Add Cloud Sync Tool
Add this to `src/tools/__init__.py`:

```python
def check_cloud_update(current_version: str) -> Dict[str, Any]:
    """Check if model update is available on cloud."""
    import requests
    try:
        response = requests.post(
            "http://YOUR_SERVER_IP:8080/api/model/check",
            json={"current_version": current_version},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def send_telemetry(agent_id: str, cpu: float, memory: float, latency: float, tools: int) -> Dict[str, Any]:
    """Send telemetry data to cloud backend."""
    import requests
    from datetime import datetime
    try:
        response = requests.post(
            "http://YOUR_SERVER_IP:8080/api/telemetry",
            json={
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": cpu,
                "memory_usage": memory,
                "inference_latency_ms": latency,
                "tool_calls": tools
            },
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}
```

---

## 🎯 Deployment Complete!

Your EdgeAgent Cloud Backend is now running on Alibaba Cloud!

### Summary:
- ✅ SAS instance created and configured
- ✅ Firewall rules set up
- ✅ Docker backend deployed
- ✅ API endpoints tested
- ✅ Web dashboard accessible
- ✅ Screenshots captured for submission

### Next Steps:
1. Record video demo showing both local agent and cloud backend
2. Add screenshots to your hackathon submission
3. Update README.md with cloud deployment information
4. Submit to Devpost before July 9, 2026 - 2 PM PT

---

## 🔧 Troubleshooting

### Issue: Cannot connect via SSH
**Solution**: 
- Verify firewall allows port 22 from your IP
- Check if password was reset and server restarted
- Try Alibaba Cloud Workbench instead

### Issue: Docker build fails
**Solution**:
```bash
# Clean up and rebuild
docker compose down
docker system prune -a
docker compose build --no-cache
```

### Issue: Port 8080 not accessible
**Solution**:
- Check firewall rules allow port 8080
- Verify Docker container is running: `docker compose ps`
- Check logs: `docker compose logs edge-agent-cloud`

### Issue: Dashboard not loading
**Solution**:
- Test health endpoint first: `curl http://YOUR_SERVER_IP:8080/health`
- Check if port 8080 is open in firewall
- Restart container: `docker compose restart`

---

## 📞 Support

For issues:
- Alibaba Cloud Documentation: https://www.alibabacloud.com/help
- Qwen Cloud Hackathon Discord: (link from hackathon page)
- GitHub Issues: Create issue in your repository
