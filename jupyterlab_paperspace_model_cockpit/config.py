"""Models configuration loading and validation."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

LOGGER = logging.getLogger(__name__)


def load_models_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        LOGGER.info("models.json not found at %s", path)
        return {}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        validate_models_config(raw)
        return raw
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Failed to parse models.json at %s: %s", path, exc)
        return {}


def resolve_model_path(root_dir: Path, model_path: str) -> Path:
    """
    Paths are resolved relative to the Jupyter server root.
    models.json does not support per-engine or per-model base directories.
    """
    path = Path(model_path)
    if path.is_absolute():
        return path
    return root_dir / path


def validate_models_config(raw: Any) -> None:
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

        allowed_keys = {
            "display_name",
            "version",
            "type",
            "source",
            "path",
            "sha256",
            "size_bytes",
        }
        _validate_allowed_keys(model, allowed_keys, f"model '{model_id}'")

        _require_str(model, "display_name", model_id)
        _require_str(model, "version", model_id)
        _require_str(model, "type", model_id)
        _require_str(model, "path", model_id)
        _require_mapping(model, "source", model_id)

        if "sha256" in model:
            _require_str(model, "sha256", model_id)
        if "size_bytes" in model:
            _require_int(model, "size_bytes", model_id)

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

        allowed_keys = {"description", "models", "auto_install", "enabled"}
        _validate_allowed_keys(bundle, allowed_keys, f"bundle '{bundle_id}'")

        _require_str(bundle, "description", bundle_id)
        _require_bool(bundle, "auto_install", bundle_id)
        _require_list_of_str(bundle, "models", bundle_id)
        if "enabled" in bundle:
            _require_bool(bundle, "enabled", bundle_id)


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
