"""Download helpers for model sources."""

from __future__ import annotations

import json
import logging
import shutil
import urllib.request
from pathlib import Path
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


def download_model(model_id: str, model: Dict[str, Any], target_path: Path) -> None:
    """
    Download policy:
    - Always write to the final target path (no temp rename)
    - On any exception, caller deletes the file
    - No resume, no partial reuse
    - File existence == installed
    Expected behavior:
    - For civitai:
      - Use model['source']['model_id'] and ['version_id']
    - For huggingface:
      - Use repo_id, filename, revision
    - Authentication, rate limiting, retries are out of scope
    """
    source = model.get("source", {})
    kind = source.get("kind")
    if kind == "civitai":
        download_civitai_model(model_id, source, target_path)
        return
    if kind == "huggingface":
        raise NotImplementedError("HuggingFace download not implemented")
    raise ValueError(f"Unknown source kind for '{model_id}'")


def download_civitai_model(model_id: str, source: Dict[str, Any], target_path: Path) -> None:
    version_id = source["version_id"]
    download_url = resolve_civitai_download_url(version_id)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Downloading '%s' from %s", model_id, download_url)

    with urllib.request.urlopen(download_url) as response, target_path.open("wb") as handle:
        shutil.copyfileobj(response, handle)

    if not target_path.exists():
        raise RuntimeError(f"Download failed for '{model_id}'")


def resolve_civitai_download_url(version_id: int) -> str:
    api_url = f"https://civitai.com/api/v1/model-versions/{version_id}"
    with urllib.request.urlopen(api_url) as response:
        payload = json.load(response)

    files = payload.get("files", [])
    if not isinstance(files, list) or not files:
        raise ValueError(f"Civitai model version {version_id} has no files")

    download_url = files[0].get("downloadUrl")
    if not isinstance(download_url, str) or not download_url:
        raise ValueError(f"Civitai model version {version_id} missing downloadUrl")

    return download_url
