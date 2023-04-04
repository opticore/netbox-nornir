"""Base NetBox plugin for interactions with AWX or Ansible Tower."""

from extras.plugins import PluginConfig


__version__ = "0.1.0"


class NetboxNornirConfig(PluginConfig):
    """Plugin configuration for netbox_nornir."""

    name = "netbox_nornir"
    verbose_name = "Netbox Nornir"
    version = __version__
    author = "OpticoreIT"
    author_email = "info@opticoreit.com"
    description = ""
    base_url = "nornir"


config = NetboxNornirConfig  # pylint: disable=invalid-name
