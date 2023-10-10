"""NetBox ORM inventory plugin."""
from typing import Any, Dict

from django.db.models import QuerySet
from django.utils.module_loading import import_string
from nornir.core.inventory import (
    ConnectionOptions,
    Defaults,
    Group,
    Groups,
    Host,
    Hosts,
    Inventory,
    ParentGroups,
)

from dcim.models import Device

from netbox_nornir.constraints import CONNECTION_ENABLE_PASSWORD_PATHS, CONNECTION_SECRETS_PATHS, PLUGIN_CFG
from netbox_nornir.exceptions import NornirNetboxException


def _set_dict_key_path(dictionary, key_path, value):
    """Set a value in a nested dictionary using a key path.

    Args:
        dictionary (dict): The dictionary to set the value in.
        key_path (str): The key path to set the value in.
    """
    *keys, last_key = key_path.split(".")
    pointer = dictionary
    for key in keys:
        pointer = pointer.setdefault(key, {})
    pointer[last_key] = value


def build_out_secret_paths(connection_options, device_secret):
    """Build out secret paths.

    Args:
        connection_options (dict): Connection options
        device_secret (str): Device secret
    """
    for nornir_provider, nornir_options in connection_options.items():
        # Offers extensibility to nornir plugins not listed in constants.py under CONNECTION_SECRETS_PATHS.
        if nornir_options.get("connection_secret_path"):
            secret_path = nornir_options.pop("connection_secret_path")
        elif CONNECTION_SECRETS_PATHS.get(nornir_provider):
            secret_path = CONNECTION_SECRETS_PATHS[nornir_provider]
        else:
            continue
        _set_dict_key_path(connection_options, secret_path, device_secret)


def build_out_enable_password_paths(connection_options, device_secret):
    """Build out enable password paths.

    Args:
        connection_options (dict): Connection options
        device_secret (str): Device secret
    """
    for nornir_provider, nornir_options in connection_options.items():
        # Offers extensibility to nornir plugins not listed in constants.py under CONNECTION_SECRETS_PATHS.
        if nornir_options.get("connection_enable_password_path"):
            secret_path = nornir_options.pop("connection_enable_password_path")
        elif CONNECTION_ENABLE_PASSWORD_PATHS.get(nornir_provider):
            secret_path = CONNECTION_ENABLE_PASSWORD_PATHS[nornir_provider]
        else:
            continue
        _set_dict_key_path(connection_options, secret_path, device_secret)


def set_host(data: Dict[str, Any], name: str, groups, host, defaults) -> Host:
    """Set host.

    Args:
        data (dict): Data
        name (str): Name
        groups (dict): Groups
        host (dict): Host
        defaults (dict): Defaults
    Returns:
        Host: Host
    """
    connection_option = {}
    for key, value in data.get("connection_options", {}).items():
        connection_option[key] = ConnectionOptions(
            hostname=value.get("hostname"),
            username=value.get("username"),
            password=value.get("password"),
            port=value.get("port"),
            platform=value.get("platform"),
            extras=value.get("extras"),
        )
    return Host(
        name=name,
        hostname=host["hostname"],
        username=host["username"],
        password=host["password"],
        platform=host["platform"],
        data=data,
        groups=groups,
        defaults=defaults,
        connection_options=connection_option,
    )


class NetboxORMInventory:
    """Construct nornir inventory from NetBox using ORM."""

    def __init__(
        self,
        queryset: QuerySet = None,
        filters: Dict = None,
        credentials_class: str = "netbox_nornir.plugins.credentials.env_vars.CredentialsEnvVars",
        credentials_params: Dict = None,
    ) -> None:
        """Initialize inventory."""
        self.queryset = queryset
        self.filters = filters

        if isinstance(credentials_class, str):
            self.cred_class = import_string(credentials_class)
        else:
            raise NornirNetboxException(
                f"A valid credentials class path (as defined by Django's import_string function) is required, but got {credentials_class} which is not importable."
            )
        self.credentials_params = credentials_params

    def load(self) -> Inventory:
        """Load inventory."""

        if isinstance(self.queryset, QuerySet) and not self.queryset:
            self.queryset = Device.objects.all()

        if self.filters:
            self.queryset = self.queryset.filter(**self.filters)

        hosts = Hosts()
        groups = Groups()
        defaults = Defaults()

        if self.credentials_params:
            cred = self.cred_class(params=self.credentials_params)
        else:
            cred = self.cred_class()

        for device in self.queryset:
            host = self.create_host(device, cred, {})

            hosts[device.name] = set_host(
                data=host["data"],
                name=host["name"],
                groups=host["groups"],
                host=host,
                defaults=defaults,
            )

            for group in hosts[device.name].groups:
                if group not in groups.keys():
                    groups[group] = Group(name=group, defaults=defaults)

        for _host in hosts.values():
            _host.groups = ParentGroups([groups[_group] for _group in _host.groups])
        for _group in groups.values():
            _group.groups = ParentGroups([groups[_group] for _group in _group.groups])

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)

    def create_host(self, device, cred, params: Dict):
        """Create host."""
        host = {"data": {}}
        if "use_fqdn" in params and params.get("use_fqdn"):
            host["hostname"] = f"{device.name}.{params.get('fqdn')}"
        else:
            if device.primary_ip:
                host["hostname"] = str(device.primary_ip.address.ip)
            else:
                host["hostname"] = device.name
        host["name"] = device.name

        if device.custom_field_data.get("access_port"):
            host["port"] = device.custom_field_data["access_port"]
        else:
            host["port"] = 22

        if not device.platform:
            raise NornirNetboxException(f"Platform missing from device {device.name}, preemptively failed.")

        host["platform"] = device.platform.napalm_driver
        host["data"]["id"] = device.id
        host["data"]["type"] = device.device_type.slug
        host["data"]["site"] = device.site.slug
        host["data"]["role"] = device.device_role.slug
        host["data"]["obj"] = device

        username, password, secret, key = cred.get_device_creds(device=device)

        host["username"] = username
        host["password"] = password
        host["data"]["secret"] = secret
        host["data"]["enable_password"] = secret
        host["data"]["key"] = key

        global_options = PLUGIN_CFG.get("connection_options", {"netmiko": {}, "napalm": {}, "scrapli": {}})

        conn_options = global_options

        build_out_secret_paths(conn_options, secret)
        build_out_enable_password_paths(conn_options, secret)

        host["data"]["connection_options"] = conn_options
        host["groups"] = self.get_host_groups(device=device)

        if device.platform.napalm_driver:
            if not host["data"]["connection_options"].get("napalm"):
                host["data"]["connection_options"]["napalm"] = {}
            host["data"]["connection_options"]["napalm"]["platform"] = device.platform.napalm_driver
        return host

    @staticmethod
    def get_host_groups(device):
        """Get the names of the groups a given device should be part of.
        Args:
            device (dcim.models.Device): Device obj
        Returns:
            (list): List of group names the device should be part of
        """
        groups = [
            "global",
            f"site__{device.site.slug}",
            f"role__{device.device_role.slug}",
            f"type__{device.device_type.slug}",
            f"manufacturer__{device.device_type.manufacturer.slug}",
        ]

        if device.platform:
            groups.append(f"platform__{device.platform.napalm_driver}")

        if device.tenant:
            groups.append(f"tenant__{device.tenant.slug}")

        return groups
