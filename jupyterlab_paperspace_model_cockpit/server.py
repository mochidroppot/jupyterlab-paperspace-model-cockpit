"""Server-side bootstrap for models.json auto-install checks."""

from __future__ import annotations

from pathlib import Path

from .auto_install import run_auto_install
from .config import load_models_config
from .handlers import register_handlers


def load_jupyter_server_extension(server_app):
    config_path = Path(server_app.root_dir) / "models.json"
    config = load_models_config(config_path)
    register_handlers(server_app)
    run_auto_install(server_app, config)
