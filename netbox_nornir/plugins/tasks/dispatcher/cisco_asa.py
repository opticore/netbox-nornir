"""network_importer driver for cisco_asa."""

from .default import NetmikoNetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Driver for Cisco ASA."""
