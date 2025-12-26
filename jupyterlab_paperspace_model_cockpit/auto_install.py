"""Auto-install orchestration based on models.json bundles."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from .config import resolve_model_path
from .downloads import download_model

LOGGER = logging.getLogger(__name__)


def run_auto_install(server_app, config: Dict[str, Any]) -> None:
    model_ids = get_auto_install_model_ids(config)
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

        target_path = resolve_model_path(root_dir, model_path)
        if target_path.exists():
            continue

        try:
            download_model(model_id, model, target_path)
        except Exception as exc:  # noqa: BLE001
            if target_path.exists():
                target_path.unlink()
            LOGGER.warning("Download failed for '%s': %s", model_id, exc)


def get_auto_install_model_ids(config: Dict[str, Any]) -> List[str]:
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
        if bundle.get("enabled", True) is False:
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
