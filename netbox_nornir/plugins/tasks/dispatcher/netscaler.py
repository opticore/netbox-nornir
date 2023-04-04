"""default network_importer driver for Netscaler."""

from .default import NetmikoNetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Collection of Nornir Tasks specific to Cisco AireOS devices."""
