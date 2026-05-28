import logging
import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers.n8n_router import router as n8n_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading FastAPI application module")

allowed_origins = [origin.strip() for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
app = FastAPI()
app.include_router(n8n_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI startup event fired")
    app.state.n8n_settings = {}

@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}