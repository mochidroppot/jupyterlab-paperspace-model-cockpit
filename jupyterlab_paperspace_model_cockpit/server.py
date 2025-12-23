"""Server-side bootstrap for models.json auto-install checks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

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
        raw = json.loads(path.read_text(encoding="utf-8"))
        _validate_models_config(raw)
        return raw
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

        try:
            _download_model(model_id, model, target_path)
        except Exception as exc:  # noqa: BLE001
            if target_path.exists():
                target_path.unlink()
            LOGGER.warning("Download failed for '%s': %s", model_id, exc)


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


def _download_model(model_id: str, model: Dict[str, Any], target_path: Path) -> None:
    """
    Download policy:
    - Always write to the final target path (no temp rename)
    - On any exception, caller deletes the file
    - No resume, no partial reuse
    - File existence == installed
    """
    LOGGER.info(
        "Download stub: would fetch model '%s' to %s", model_id, target_path
    )
    raise NotImplementedError("Download not implemented")


def _validate_models_config(raw: Any) -> None:
    if not isinstance(raw, dict):
        raise ValueError("models.json must be an object")

    allowed_top_keys = {"models", "bundles"}
    _validate_allowed_keys(raw, allowed_top_keys, "models.json")

    if "models" in raw:
        _validate_models_section(raw["models"])
    if "bundles" in raw:
        _validate_bundles_section(raw["bundles"])


def _validate_models_section(models: Any) -> None:
    if not isinstance(models, dict):
        raise ValueError("'models' must be an object")

    for model_id, model in models.items():
        if not isinstance(model_id, str) or not model_id:
            raise ValueError("model ids must be non-empty strings")
        if not isinstance(model, dict):
            raise ValueError(f"model '{model_id}' must be an object")

        allowed_keys = {"display_name", "version", "type", "source", "path"}
        _validate_allowed_keys(model, allowed_keys, f"model '{model_id}'")

        _require_str(model, "display_name", model_id)
        _require_str(model, "version", model_id)
        _require_str(model, "type", model_id)
        _require_str(model, "path", model_id)
        _require_mapping(model, "source", model_id)

        _validate_source(model["source"], model_id)


def _validate_source(source: Any, model_id: str) -> None:
    if not isinstance(source, dict):
        raise ValueError(f"model '{model_id}' source must be an object")

    if "kind" not in source:
        raise ValueError(f"model '{model_id}' source missing kind")
    if source["kind"] not in {"civitai", "huggingface"}:
        raise ValueError(f"model '{model_id}' source kind must be civitai or huggingface")

    if source["kind"] == "civitai":
        allowed_keys = {"kind", "model_id", "version_id"}
        _validate_allowed_keys(source, allowed_keys, f"model '{model_id}' source")
        _require_int(source, "model_id", model_id)
        _require_int(source, "version_id", model_id)
        return

    allowed_keys = {"kind", "repo_id", "filename", "revision"}
    _validate_allowed_keys(source, allowed_keys, f"model '{model_id}' source")
    _require_str(source, "repo_id", model_id)
    _require_str(source, "filename", model_id)
    _require_str(source, "revision", model_id)


def _validate_bundles_section(bundles: Any) -> None:
    if not isinstance(bundles, dict):
        raise ValueError("'bundles' must be an object")

    for bundle_id, bundle in bundles.items():
        if not isinstance(bundle_id, str) or not bundle_id:
            raise ValueError("bundle ids must be non-empty strings")
        if not isinstance(bundle, dict):
            raise ValueError(f"bundle '{bundle_id}' must be an object")

        allowed_keys = {"description", "models", "auto_install"}
        _validate_allowed_keys(bundle, allowed_keys, f"bundle '{bundle_id}'")

        _require_str(bundle, "description", bundle_id)
        _require_bool(bundle, "auto_install", bundle_id)
        _require_list_of_str(bundle, "models", bundle_id)


def _validate_allowed_keys(obj: Mapping[str, Any], allowed: Sequence[str], label: str) -> None:
    extra = set(obj.keys()) - set(allowed)
    if extra:
        raise ValueError(f"{label} has unexpected keys: {sorted(extra)}")


def _require_str(obj: Mapping[str, Any], key: str, label: str) -> None:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} missing or invalid '{key}'")


def _require_int(obj: Mapping[str, Any], key: str, label: str) -> None:
    value = obj.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{label} missing or invalid '{key}'")


def _require_bool(obj: Mapping[str, Any], key: str, label: str) -> None:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{label} missing or invalid '{key}'")


def _require_mapping(obj: Mapping[str, Any], key: str, label: str) -> None:
    value = obj.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{label} missing or invalid '{key}'")


def _require_list_of_str(obj: Mapping[str, Any], key: str, label: str) -> None:
    value = obj.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} missing or invalid '{key}'")
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{label} has invalid entry in '{key}'")
