# Backend - FastAPI Service

FastAPI backend service for n8n workflow automation and LLM integration.

## 🚀 Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running the Server

**Development (with auto-reload)**
```bash
uvicorn app.main:app --reload
```

**Production**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok"}
```

## 📁 Project Structure

```
backend/
├── app/
│   └── main.py          # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container definition
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

The following environment variables should be set (see `.env` at project root):

- `N8N_BASE_URL` - URL of the n8n workflow engine
- `N8N_API_KEY` - API key for n8n authentication
- `LLM_API_KEY` - API key for Language Model service

## 📦 Dependencies

- **fastapi** - Modern Python web framework
- **uvicorn** - ASGI server for FastAPI

See [requirements.txt](requirements.txt) for exact versions.

## 🐳 Docker

### Build

```bash
docker build -t n8nproject-backend .
```

### Run

```bash
docker run -p 8000:8000 \
  -e N8N_BASE_URL=<url> \
  -e N8N_API_KEY=<key> \
  -e LLM_API_KEY=<key> \
  n8nproject-backend
```

## 🔌 API Endpoints

- `GET /health` - Health check endpoint

## 📝 Development Notes

- Current version uses minimal dependencies (fastapi, uvicorn)
- Ready for expansion with additional endpoints and services
- SSR support through Express server in frontend handles frontend routing

## 🚀 Deployment

### Render.com

Automatically deploys from this directory. See `render.yaml` in project root for configuration.

### Docker Compose

Runs on port 8000. See `docker-compose.yml` in project root.
