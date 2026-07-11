# 🚀 Render.com Deployment Guide for EdgeAgent

## Overview

This guide walks you through deploying the **EdgeAgent Cloud Backend** on **Render.com** (Free Tier). Render.com is perfect for hackathons - no credit card required, Docker support, and free hosting.

The backend provides:
- Model registry API (check for updates)
- Telemetry logging (track agent performance)
- Health check endpoint
- Web-based status dashboard

---

## 📋 Prerequisites

- GitHub account (free at github.com)
- Render.com account (free, no card required)
- EdgeAgent project with `cloud_backend/` folder

---

## Step 1: Prepare Your GitHub Repository

### 1.1 Create a GitHub Repository (If You Haven't Already)

1. Go to **https://github.com**
2. Click **New Repository**
3. Repository name: `edge-agent`
4. Description: "On-Device AI Assistant for Qwen Cloud AI Hackathon"
5. Visibility: **Public** (required for hackathon submission)
6. Click **Create Repository**

### 1.2 Upload Your Code

**Option A: Using GitHub Desktop (Easiest)**
1. Download **GitHub Desktop** from https://desktop.github.com
2. Clone your new repository
3. Copy all EdgeAgent files to the repository folder
4. Commit and push to GitHub

**Option B: Using Web Upload**
1. Go to your repository on GitHub
2. Click **Add files** → **Upload files**
3. Drag and drop these folders/files:
   - `cloud_backend/` (entire folder)
   - `README.md`
   - `LICENSE` (create one, see below)
4. Click **Commit changes**

**Option C: Using Git Command Line**
```bash
cd C:\Savio\My_QWEN_Project\edge-agent
git init
git remote add origin https://github.com/YOUR_USERNAME/edge-agent.git
git add .
git commit -m "Initial commit: EdgeAgent for Qwen Cloud Hackathon"
git branch -M main
git push -u origin main
```

### 1.3 Add LICENSE File (Required for Hackathon)

Create a file named `LICENSE` in your repository root with this content:

```
MIT License

Copyright (c) 2026 EdgeAgent Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Step 2: Sign Up for Render.com

### 2.1 Create Account
1. Go to **https://render.com**
2. Click **Sign Up** (top-right corner)
3. Choose **Sign up with GitHub** (recommended) or use email
4. **No credit card required!**

### 2.2 Verify Email
- Check your email for verification link
- Click the verification link
- You're now logged into Render.com

---

## Step 3: Create Your Web Service

### 3.1 Start New Service
1. Click **New +** button (top-right)
2. Select **Web Service**

### 3.2 Connect Repository
1. You'll see: **"Connect a repository"**
2. Click **Connect Repository** next to your `edge-agent` repo
3. Render will scan for Dockerfiles

### 3.3 Configure Web Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `edge-agent-cloud` |
| **Region** | Singapore (closest to you) |
| **Branch** | `main` |
| **Root Directory** | `cloud_backend` |
| **Runtime** | `Docker` |
| **Build Command** | (leave blank) |
| **Start Command** | (leave blank - uses Dockerfile) |
| **Instance Type** | **Free** |

### 3.4 Advanced Settings (Optional)
- **Auto-Deploy**: ✅ Enabled (recommended - auto-updates on git push)
- **Health Check Path**: `/health`

### 3.5 Create Service
1. Click **Create Web Service**
2. Wait 5-10 minutes for build and deployment

---

## Step 4: Monitor Deployment

### 4.1 Check Build Logs
1. Go to your service dashboard
2. Click **Logs** tab
3. Watch the build progress:
   ```
   Building Docker image...
   Installing dependencies...
   Starting application...
   Deployment complete!
   ```

### 4.2 Get Your Live URL
After deployment completes, you'll see:
- **Service URL**: `https://edge-agent-cloud-xxxx.onrender.com`
- Copy this URL - you'll need it for testing and submission!

---

## Step 5: Test Your Deployment

### 5.1 Test Health Endpoint
Open browser or use curl:
```
https://edge-agent-cloud-xxxx.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-07-04T12:00:00",
  "version": "1.0.0"
}
```

### 5.2 Test Model Check API
```bash
curl -X POST https://edge-agent-cloud-xxxx.onrender.com/api/model/check \
  -H "Content-Type: application/json" \
  -d '{"current_version": "qwen2.5-0.5b-instruct"}'
```

### 5.3 Access Web Dashboard
Open your browser:
```
https://edge-agent-cloud-xxxx.onrender.com/dashboard
```

You should see the EdgeAgent Cloud Dashboard with status information!

### 5.4 Test Telemetry Logging
```bash
curl -X POST https://edge-agent-cloud-xxxx.onrender.com/api/telemetry \
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

## Step 6: Capture Screenshots for Hackathon Submission

### 6.1 Required Screenshots

Take screenshots of:

1. **Render.com Dashboard**: Show your service with "Live" status
2. **Service URL**: Browser showing your live URL
3. **Health Check**: Browser showing `/health` response
4. **Web Dashboard**: Browser showing `/dashboard` with stats
5. **Build Logs**: Terminal showing successful deployment
6. **GitHub Repository**: Show your public repo with all files

### 6.2 Save Screenshots
Save all screenshots in:
```
C:\Savio\My_QWEN_Project\edge-agent\docs\render-screenshots\
```

---

## Step 7: Update Local EdgeAgent (Optional)

To make your local EdgeAgent communicate with the Render cloud backend:

### 7.1 Add Cloud Sync Tool
Add this to `src/tools/__init__.py`:

```python
def check_cloud_update(current_version: str) -> Dict[str, Any]:
    """Check if model update is available on cloud."""
    import requests
    try:
        response = requests.post(
            "https://YOUR-RENDER-URL.onrender.com/api/model/check",
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
            "https://YOUR-RENDER-URL.onrender.com/api/telemetry",
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

Replace `YOUR-RENDER-URL` with your actual Render service URL.

---

## 🎯 Deployment Complete!

Your EdgeAgent Cloud Backend is now running on Render.com!

### Summary:
- ✅ GitHub repository created and public
- ✅ Render.com account created (no card)
- ✅ Web service deployed on free tier
- ✅ API endpoints tested
- ✅ Web dashboard accessible
- ✅ Screenshots captured for submission

### Important Notes:
- **Free Tier Limit**: 750 hours/month (enough for continuous running)
- **Auto-Sleep**: Free services may sleep after 15 minutes of inactivity
- **Wake-Up**: First request after sleep takes ~30 seconds to respond
- **Solution**: Use a free uptime monitor (like UptimeRobot) to ping your service every 10 minutes

---

## 🔧 Troubleshooting

### Issue: Build Fails
**Solution**:
- Check that `cloud_backend/` folder contains all required files
- Verify `Dockerfile` is in the root of `cloud_backend/`
- Check build logs for specific error messages

### Issue: Service Shows "Crashed"
**Solution**:
- Check logs for error messages
- Verify `main.py` starts correctly: `uvicorn main:app --host 0.0.0.0 --port 8080`
- Ensure `requirements.txt` has all dependencies

### Issue: 502 Bad Gateway
**Solution**:
- Service is still starting up (wait 2-3 minutes)
- Service may have crashed - check logs
- Free tier may be at capacity - try again later

### Issue: Service Goes to Sleep
**Solution**:
- Sign up for **UptimeRobot** (free at uptimerobot.com)
- Create a monitor that pings your `/health` endpoint every 5 minutes
- This keeps your service awake continuously

---

## 📞 Support

For issues:
- Render.com Documentation: https://render.com/docs
- Render.com Community: https://community.render.com
- GitHub Issues: Create issue in your repository

---

## 🏆 Hackathon Submission Notes

### For the "Proof of Cloud Deployment" Requirement:

Since you deployed on Render.com instead of Alibaba Cloud (due to payment verification requirements), include this explanation in your submission:

```markdown
## Cloud Deployment

**Deployment Platform**: Render.com (Free Tier)

**Why Render.com Instead of Alibaba Cloud?**
- Alibaba Cloud account verification requires credit/debit card
- Render.com provides equivalent functionality without card requirement
- Same Docker-based architecture works on both platforms
- Code is cloud-agnostic and production-ready

**Live Deployment**:
- URL: https://edge-agent-cloud-xxxx.onrender.com
- Status: Live and operational
- Endpoints: /health, /dashboard, /api/model/check, /api/telemetry

**Alibaba Cloud Compatibility**:
- Complete deployment guide created: `ALIBABA_DEPLOYMENT_GUIDE.md`
- Docker container runs identically on Alibaba Cloud SAS
- Ready for migration once verification is complete
- $40 Alibaba Cloud coupon available for future deployment
```

This shows judges that you:
1. Built a real, working cloud deployment
2. Have Alibaba Cloud infrastructure ready (code + guide)
3. Made a practical decision based on verification constraints
4. Created cloud-agnostic, production-ready code
