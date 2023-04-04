"""default network_importer driver for Juniper."""

from .default import NetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Collection of Nornir Tasks specific to Juniper Junos devices."""
