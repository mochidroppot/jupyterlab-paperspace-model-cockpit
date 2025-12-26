"""HTTP handlers for model cockpit APIs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from tornado import web

from .config import load_models_config, resolve_model_path


def register_handlers(server_app) -> None:
    web_app = server_app.web_app
    base_url = web_app.settings.get("base_url", "/")
    models_url = url_path_join(base_url, "paperspace-model-cockpit", "api", "models")
    web_app.add_handlers(".*$", [(models_url, ModelsHandler)])


class ModelsHandler(APIHandler):
    @web.authenticated
    def get(self) -> None:
        config_path = Path(self.serverapp.root_dir) / "models.json"
        config = load_models_config(config_path)
        payload = build_models_payload(config, Path(self.serverapp.root_dir))
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(payload))


def build_models_payload(config: Dict[str, Any], root_dir: Path) -> Dict[str, Any]:
    models = config.get("models", {})
    if not isinstance(models, dict):
        return {"models": []}

    items = []
    for model_id, model in models.items():
        if not isinstance(model, dict):
            continue

        model_path = model.get("path")
        installed = False
        if isinstance(model_path, str) and model_path:
            target_path = resolve_model_path(root_dir, model_path)
            installed = target_path.exists()

        items.append(
            {
                "id": model_id,
                "display_name": model.get("display_name"),
                "version": model.get("version"),
                "type": model.get("type"),
                "path": model_path,
                "installed": installed,
                "source": model.get("source"),
            }
        )

    return {"models": items}
