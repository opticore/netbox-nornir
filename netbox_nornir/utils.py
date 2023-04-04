"""Utilities for plugin."""
import logging
from typing import Any

from netbox_nornir.plugins.tasks.dispatcher import _DEFAULT_DRIVERS_MAPPING
from netbox_nornir.constraints import PLUGIN_CFG


def get_dispatcher():
    """Helper method to load the dispatcher from netbox nornir or config if defined."""
    if PLUGIN_CFG.get("dispatcher_mapping"):
        return {**_DEFAULT_DRIVERS_MAPPING, **PLUGIN_CFG["dispatcher_mapping"]}
    return _DEFAULT_DRIVERS_MAPPING


class NornirLogger:
    """Similar to a mixin, to utilize Python logging and Jobs Result obj."""

    def __init__(self, name: str, netbox_job=None, debug: bool = False):
        """Initialize the object."""
        self.logger = logging.getLogger(name)
        self.debug = debug
        self.netbox_job = netbox_job

    def log_debug(self, message: str, grouping: str = "main"):
        """Debug, does not take obj, and only logs to jobs result when in global debug mode."""
        if self.netbox_job and self.debug:
            self.netbox_job.log_debug(message, grouping=grouping)
        self.logger.debug(message)

    def log_info(self, obj: Any, message: str, grouping: str = "main"):
        """Log to Python logger and jogs results for info messages."""
        if self.netbox_job:
            self.netbox_job.log_info(message, grouping=grouping)
        self.logger.info("%s | %s", str(obj), message)

    def log_success(self, obj: Any, message: str, grouping: str = "main"):
        """Log to Python logger and jogs results for success messages."""
        if self.netbox_job:
            self.netbox_job.log_success(message, grouping=grouping)
        self.logger.info("%s | %s", str(obj), message)

    def log_warning(self, obj: Any, message: str, grouping: str = "main"):
        """Log to Python logger and jogs results for warning messages."""
        if self.netbox_job:
            self.netbox_job.log_warning(message, grouping=grouping)
        self.logger.warning("%s | %s", str(obj), message)

    def log_failure(self, obj: Any, message: str, grouping: str = "main"):
        """Log to Python logger and jogs results for failure messages."""
        if self.netbox_job:
            self.netbox_job.log_failure(message, grouping=grouping)
        self.logger.error("%s | %s", str(obj), message)
