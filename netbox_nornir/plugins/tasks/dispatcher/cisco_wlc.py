"""default network_importer driver for Cisco AireOS."""

from .default import NetmikoNetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Collection of Nornir Tasks specific to Cisco AireOS devices."""
