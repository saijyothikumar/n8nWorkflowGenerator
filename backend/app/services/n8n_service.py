from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

CACHE_FILE = Path(tempfile.gettempdir()) / "n8n_node_types_cache.json"
_node_types_cache: Dict[str, Any] = {}


def _cache_key(base_url: str, api_key: str) -> str:
    return json.dumps([base_url.rstrip("/"), api_key], sort_keys=True)


def _load_node_types_cache_from_disk() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {}

    try:
        with CACHE_FILE.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if isinstance(raw, dict):
            return raw
        logger.warning("Node types cache file has unexpected format, ignoring")
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Unable to load n8n node types cache from disk: %s", exc)
    return {}


def _save_node_types_cache_to_disk() -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CACHE_FILE.open("w", encoding="utf-8") as handle:
            json.dump(_node_types_cache, handle)
    except OSError as exc:
        logger.warning("Unable to persist n8n node types cache to disk: %s", exc)


class N8NService:
    """Lightweight n8n client that maintains an AsyncClient and credentials."""

    def __init__(self) -> None:
        self.base_url: Optional[str] = None
        self.api_key: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    def _headers(self) -> Dict[str, str]:
        return {
            "X-N8N-API-KEY": self.api_key or "",
            "Content-Type": "application/json",
        }

    async def _ensure_client(self) -> httpx.AsyncClient:
        normalized_base_url = self.base_url or ""
        current_base_url = str(self._client.base_url) if self._client is not None else ""

        if self._client is None or current_base_url != normalized_base_url:
            if self._client is not None:
                await self._client.aclose()
            self._client = httpx.AsyncClient(base_url=normalized_base_url, timeout=10.0)

        return self._client

    async def connect(self, base_url: str, api_key: str) -> Dict[str, Any]:
        """Store credentials and verify connectivity to the n8n instance.

        Performs a GET /api/v1/workflows?limit=1 as a smoke test.

        Returns a dict: {"success": bool, ...}
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

        client = await self._ensure_client()
        headers = self._headers()

        try:
            url = "/api/v1/workflows"
            logger.info("Testing n8n connection to %s", self.base_url)
            resp = await client.get(url, params={"limit": 1}, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return {"success": True, "status_code": resp.status_code, "data": data}
        except httpx.HTTPStatusError as e:
            logger.warning("n8n returned non-2xx status: %s", e.response.status_code)
            text = e.response.text if e.response is not None else str(e)
            return {
                "success": False,
                "status_code": e.response.status_code if e.response is not None else None,
                "error": text,
            }
        except httpx.RequestError as e:
            logger.error("Request error when connecting to n8n: %s", str(e))
            return {"success": False, "error": str(e)}

    async def fetch_node_types(self, base_url: str, api_key: str) -> Dict[str, Any]:
        """Fetch n8n node types, caching them in-session and on disk."""
        normalized_base_url = base_url.rstrip("/")
        key = _cache_key(normalized_base_url, api_key)

        if key in _node_types_cache:
            logger.info("Returning cached n8n node types for %s", normalized_base_url)
            return {"success": True, "cached": True, "data": _node_types_cache[key]}

        self.base_url = normalized_base_url
        self.api_key = api_key
        client = await self._ensure_client()
        headers = self._headers()

        try:
            url = "/api/v1/node-types"
            logger.info("Fetching n8n node types from %s", self.base_url)
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            count = len(data) if isinstance(data, (list, tuple)) else len(data.get("data", [])) if isinstance(data, dict) else None
            logger.info("Fetched %s n8n node types from %s", count, self.base_url)
            _node_types_cache[key] = data
            _save_node_types_cache_to_disk()
            return {"success": True, "cached": False, "status_code": resp.status_code, "data": data}
        except httpx.HTTPStatusError as e:
            logger.warning("n8n returned non-2xx status while fetching node types: %s", e.response.status_code)
            text = e.response.text if e.response is not None else str(e)
            return {
                "success": False,
                "status_code": e.response.status_code if e.response is not None else None,
                "error": text,
            }
        except httpx.RequestError as e:
            logger.error("Request error when fetching n8n node types: %s", str(e))
            return {"success": False, "error": str(e)}

    async def push_workflow(self, base_url: str, api_key: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow in n8n by posting the workflow JSON."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        client = await self._ensure_client()
        headers = self._headers()

        try:
            url = "/api/v1/workflows"
            logger.info("Pushing new n8n workflow to %s", self.base_url)
            resp = await client.post(url, json=workflow_json, headers=headers)
            resp.raise_for_status()
            return {"success": True, "status_code": resp.status_code, "data": resp.json()}
        except httpx.HTTPStatusError as e:
            logger.warning("n8n returned non-2xx status when pushing workflow: %s", e.response.status_code)
            error_payload: Any = None
            try:
                error_payload = e.response.json() if e.response is not None else None
            except ValueError:
                error_payload = e.response.text if e.response is not None else str(e)
            return {
                "success": False,
                "status_code": e.response.status_code if e.response is not None else None,
                "error": error_payload,
            }
        except httpx.RequestError as e:
            logger.error("Request error when pushing workflow: %s", str(e))
            return {"success": False, "error": str(e)}

    async def update_workflow(self, base_url: str, api_key: str, workflow_id: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow in n8n by PATCHing workflow JSON."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        client = await self._ensure_client()
        headers = self._headers()

        try:
            url = f"/api/v1/workflows/{workflow_id}"
            logger.info("Updating n8n workflow %s at %s", workflow_id, self.base_url)
            resp = await client.patch(url, json=workflow_json, headers=headers)
            resp.raise_for_status()
            return {"success": True, "status_code": resp.status_code, "data": resp.json()}
        except httpx.HTTPStatusError as e:
            logger.warning("n8n returned non-2xx status when updating workflow: %s", e.response.status_code)
            error_payload: Any = None
            try:
                error_payload = e.response.json() if e.response is not None else None
            except ValueError:
                error_payload = e.response.text if e.response is not None else str(e)
            return {
                "success": False,
                "status_code": e.response.status_code if e.response is not None else None,
                "error": error_payload,
            }
        except httpx.RequestError as e:
            logger.error("Request error when updating workflow: %s", str(e))
            return {"success": False, "error": str(e)}

    def get_node_schema(self, node_type_name: str, base_url: Optional[str] = None, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Return the cached schema for a specific node type name."""
        if base_url is None or api_key is None:
            base_url = self.base_url
            api_key = self.api_key

        if not base_url or not api_key:
            logger.warning("get_node_schema called without cached base_url/api_key")
            return None

        key = _cache_key(base_url, api_key)
        node_types = _node_types_cache.get(key)
        if not isinstance(node_types, (list, tuple)):
            node_types = node_types.get("data") if isinstance(node_types, dict) else None

        if isinstance(node_types, list):
            for node in node_types:
                if node.get("name") == node_type_name:
                    return node
        return None

    def search_nodes(self, keyword: str, base_url: Optional[str] = None, api_key: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """Search cached node display names and descriptions for a keyword."""
        if base_url is None or api_key is None:
            base_url = self.base_url
            api_key = self.api_key

        if not base_url or not api_key:
            logger.warning("search_nodes called without cached base_url/api_key")
            return {"success": False, "error": "missing base_url or api_key"}

        key = _cache_key(base_url, api_key)
        node_types = _node_types_cache.get(key)
        if not isinstance(node_types, (list, tuple)):
            node_types = node_types.get("data") if isinstance(node_types, dict) else None

        if not isinstance(node_types, list):
            return {"success": False, "error": "node types not cached"}

        query = keyword.strip().lower()
        matches = []
        for node in node_types:
            display_name = str(node.get("displayName", "")).lower()
            description = str(node.get("description", "")).lower()
            score = 0
            if query in display_name:
                score += 2
            if query in description:
                score += 1
            if score > 0:
                matches.append((score, node))

        matches.sort(key=lambda item: (-item[0], str(item[1].get("displayName", ""))))
        return {"success": True, "results": [node for _, node in matches[:limit]]}

    def get_node_categories(self, base_url: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Return a deduplicated list of node categories from the cached node types."""
        if base_url is None or api_key is None:
            base_url = self.base_url
            api_key = self.api_key

        if not base_url or not api_key:
            logger.warning("get_node_categories called without cached base_url/api_key")
            return {"success": False, "error": "missing base_url or api_key"}

        key = _cache_key(base_url, api_key)
        node_types = _node_types_cache.get(key)
        if not isinstance(node_types, (list, tuple)):
            node_types = node_types.get("data") if isinstance(node_types, dict) else None

        if not isinstance(node_types, list):
            return {"success": False, "error": "node types not cached"}

        categories = []
        seen = set()
        for node in node_types:
            category = node.get("group") or node.get("category") or node.get("displayName")
            if isinstance(category, str):
                category = category.strip()
            else:
                category = None
            if category and category not in seen:
                seen.add(category)
                categories.append(category)

        return {"success": True, "categories": categories}

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


_node_types_cache = _load_node_types_cache_from_disk()

# Module-level singleton for convenience
n8n_service = N8NService()


__all__ = ["N8NService", "n8n_service"]
