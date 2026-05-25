import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading FastAPI application module")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI startup event fired")

@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}