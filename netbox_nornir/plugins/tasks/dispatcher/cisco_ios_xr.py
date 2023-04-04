"""network_importer driver for cisco IOS-XR."""

from .default import NetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Driver for Cisco IOS-XR."""
