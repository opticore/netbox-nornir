"""network_importer driver for arista_eos."""

from .default import NetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Collection of Nornir Tasks specific to Arista EOS devices."""
