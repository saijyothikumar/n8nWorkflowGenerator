# N8N Project

A full-stack web application combining Angular frontend with FastAPI backend for n8n workflow automation and LLM integration.

## 📁 Project Structure

```
n8nproject/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/app/         # Angular web application
│   ├── src/
│   ├── package.json
│   ├── angular.json
│   └── Dockerfile
├── docker-compose.yml    # Multi-container orchestration
├── render.yaml          # Render.com deployment config
├── vercel.json          # Vercel deployment config
└── .env                 # Environment variables (local)
```

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose

### Development

**1. Setup Environment Variables**
```bash
cp .env.example .env
# Edit .env with your values
```

**2. Run with Docker Compose**
```bash
docker-compose up
```

**3. Or run services separately:**

**Backend (FastAPI)**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API: http://localhost:8000
# Health check: http://localhost:8000/health
```

**Frontend (Angular)**
```bash
cd frontend/app
npm install
npm start
# App: http://localhost:4200
```

## 🌐 Deployment

### Render.com (Backend)
- Automatically deploys from `backend/` directory
- Environment variables configured in Render dashboard
- Python runtime 3.11

### Vercel (Frontend)
- Automatically deploys from `frontend/app/` directory
- Static site with Server-Side Rendering (SSR)
- Environment variables configured in Vercel dashboard

### Docker
Both services have Dockerfiles for containerized deployment:
```bash
docker build -t n8nproject-backend backend/
docker build -t n8nproject-frontend frontend/app/
```

## 📦 Environment Variables

See [.env.example](.env.example) for all required environment variables:
- `N8N_BASE_URL` - n8n workflow engine URL
- `N8N_API_KEY` - n8n API authentication key
- `LLM_API_KEY` - Language Model API key

## 🏗️ Technology Stack

**Frontend**
- Angular 21.2
- TypeScript 5.9
- Server-Side Rendering (SSR)
- Express for SSR server

**Backend**
- FastAPI
- Python 3.11
- Uvicorn

**DevOps**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Render.com (Backend hosting)
- Vercel (Frontend hosting)

## 🔧 Development

### Frontend Development
```bash
cd frontend/app
npm run dev      # Development server
npm run build    # Production build
npm run lint     # ESLint
npm run format   # Prettier formatting
```

### Backend Development
```bash
cd backend
# Development (with auto-reload)
uvicorn app.main:app --reload
# Production
uvicorn app.main:app --host 0.0.0.0
```

## 📝 Components

- **Chat Panel** - User interface for chat interactions
- **Graph Panel** - Visualization of workflow graphs

## 🔄 CI/CD

GitHub Actions workflow runs on each push:
- Backend: Python syntax validation + Docker build
- Frontend: Dependency installation + linting + build

## 📄 License

MIT


