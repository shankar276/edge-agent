# EdgeAgent Cloud Backend

Lightweight FastAPI backend for EdgeAgent cloud services.

## Features
- Model registry API (check for updates)
- Telemetry logging (track agent performance)
- Health check endpoint
- Web-based status dashboard

## Files
- `main.py` - FastAPI application with all API endpoints
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Docker orchestration

## Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

Access dashboard at: http://localhost:8080/dashboard

## Deployment
See `../ALIBABA_DEPLOYMENT_GUIDE.md` for step-by-step instructions.

## API Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/model/check` - Check for model updates
- `POST /api/telemetry` - Log telemetry data
- `GET /api/telemetry/stats` - Get telemetry statistics
- `GET /dashboard` - Web dashboard
