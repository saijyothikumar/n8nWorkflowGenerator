import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers.n8n_router import router as n8n_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading FastAPI application module")

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

env_path = Path(__file__).resolve().parents[2] / ".env"
if load_dotenv:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info("Loaded environment from %s", env_path)
    else:
        logger.info("No .env file found at %s; using process environment only", env_path)
else:
    logger.info("python-dotenv not installed; using process environment only")

allowed_origins = [origin.strip() for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
if not allowed_origins:
    logger.warning("ALLOWED_ORIGINS is not configured; CORS will deny all origins. Set ALLOWED_ORIGINS in your environment or .env file.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI startup event fired")
    app.state.n8n_settings = {}
    yield
    # Shutdown (if needed in the future)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(n8n_router)



@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}