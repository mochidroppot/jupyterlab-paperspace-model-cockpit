"""Server-side bootstrap for models.json auto-install checks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

LOGGER = logging.getLogger(__name__)


def load_jupyter_server_extension(server_app):
    config_path = Path(server_app.root_dir) / "models.json"
    config = _load_models_config(config_path)
    _run_auto_install(server_app, config)


def _load_models_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        LOGGER.info("models.json not found at %s", path)
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Failed to parse models.json at %s: %s", path, exc)
        return {}


def _run_auto_install(server_app, config: Dict[str, Any]) -> None:
    model_ids = _get_auto_install_model_ids(config)
    if not model_ids:
        return

    models = config.get("models", {})
    if not isinstance(models, dict):
        LOGGER.warning("models.json has invalid 'models' section")
        return

    root_dir = Path(server_app.root_dir)

    for model_id in model_ids:
        model = models.get(model_id)
        if not isinstance(model, dict):
            LOGGER.warning("Model id '%s' not found in models.json", model_id)
            continue

        model_path = model.get("path")
        if not isinstance(model_path, str) or not model_path:
            LOGGER.warning("Model '%s' missing valid path", model_id)
            continue

        target_path = _resolve_model_path(root_dir, model_path)
        if target_path.exists():
            continue

        _download_model_stub(model_id, model, target_path)


def _get_auto_install_model_ids(config: Dict[str, Any]) -> List[str]:
    bundles = config.get("bundles", {})
    if not isinstance(bundles, dict):
        LOGGER.warning("models.json has invalid 'bundles' section")
        return []

    ordered: List[str] = []
    seen = set()

    for bundle_id, bundle in bundles.items():
        if not isinstance(bundle, dict):
            LOGGER.warning("Bundle '%s' is not an object", bundle_id)
            continue
        if not bundle.get("auto_install", False):
            continue

        models = bundle.get("models", [])
        if not isinstance(models, list):
            LOGGER.warning("Bundle '%s' has invalid models list", bundle_id)
            continue

        for model_id in models:
            if not isinstance(model_id, str):
                continue
            if model_id in seen:
                continue
            seen.add(model_id)
            ordered.append(model_id)

    return ordered


def _resolve_model_path(root_dir: Path, model_path: str) -> Path:
    path = Path(model_path)
    if path.is_absolute():
        return path
    return root_dir / path


def _download_model_stub(model_id: str, model: Dict[str, Any], target_path: Path) -> None:
    LOGGER.info(
        "Download stub: would fetch model '%s' to %s", model_id, target_path
    )
