from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.services.n8n_service import n8n_service

router = APIRouter(prefix="/api/n8n", tags=["n8n"])


class N8NConnectRequest(BaseModel):
    n8n_url: str
    api_key: str


class PushWorkflowRequest(BaseModel):
    workflow_json: Dict[str, Any]


def _get_n8n_settings(request: Request) -> Dict[str, str]:
    settings = getattr(request.app.state, "n8n_settings", None)
    if not settings or "base_url" not in settings or "api_key" not in settings:
        raise HTTPException(status_code=400, detail="N8N connection is not configured")
    return settings


@router.post("/connect")
async def connect_n8n(payload: N8NConnectRequest, request: Request) -> Dict[str, Any]:
    result = await n8n_service.connect(payload.n8n_url, payload.api_key)
    if result.get("success"):
        request.app.state.n8n_settings = {
            "base_url": payload.n8n_url.rstrip("/"),
            "api_key": payload.api_key,
        }
        # Synchronously fetch and cache node types to prevent race condition
        # when get_node_categories is called immediately after connect
        await n8n_service.fetch_node_types(payload.n8n_url, payload.api_key)
    return result


@router.get("/node-types")
async def get_node_types(request: Request) -> Dict[str, Any]:
    settings = _get_n8n_settings(request)
    return await n8n_service.fetch_node_types(settings["base_url"], settings["api_key"])


@router.get("/node-categories")
async def get_node_categories(request: Request) -> Dict[str, Any]:
    settings = _get_n8n_settings(request)
    return n8n_service.get_node_categories(settings["base_url"], settings["api_key"])


@router.post("/push")
async def push_workflow(payload: PushWorkflowRequest, request: Request) -> Dict[str, Any]:
    settings = _get_n8n_settings(request)
    return await n8n_service.push_workflow(settings["base_url"], settings["api_key"], payload.workflow_json)
