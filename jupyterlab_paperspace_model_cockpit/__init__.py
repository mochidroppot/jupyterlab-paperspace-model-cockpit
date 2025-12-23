"""JupyterLab Paperspace Model Cockpit server extension."""

from ._version import __version__


def _jupyter_server_extension_points():
    return [{"module": "jupyterlab_paperspace_model_cockpit.server"}]
