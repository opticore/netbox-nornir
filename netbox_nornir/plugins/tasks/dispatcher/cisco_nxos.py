"""network_importer driver for cisco NXOS."""

from .default import NetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Driver for Cisco NXOS."""
