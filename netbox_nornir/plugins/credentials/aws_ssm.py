"""Nornir plugin to retrieve credentials from AWS SSM Parameter Store."""

import boto3
import os
from botocore.client import Config
from dcim.models import Device

from .base import BaseCredentials


class CredentialsAwsSsm(BaseCredentials):
    """Nornir plugin to retrieve credentials from AWS SSM Parameter Store."""

    def __init__(self, params={}):  # pylint: disable=dangerous-default-value
        """Init."""
        config = Config(connect_timeout=15, retries={"max_attempts": 0})
        self.client = boto3.client("ssm", config=config, region_name=os.environ.get("AWS_REGION", "eu-west-2"))
        self.params = params
        self.username = None
        self.password = None
        self.secret = None
        self.key = None

    def build_parameter_names(self, device_name, manufacturer, platform):
        """Build a list of parameter names to try."""
        prefix = "/netbox"
        # Ordered list of parameter names to try
        return [
            "/".join([prefix, device_name, "username"]),
            "/".join([prefix, device_name, "password"]),
            "/".join([prefix, device_name, "secret"]),
            "/".join([prefix, device_name, "key"]),
            "/".join(
                [
                    prefix,
                    f"{manufacturer.lower()}_{platform.lower()}",
                    "username",
                ]
            ),
            "/".join(
                [
                    prefix,
                    f"{manufacturer.lower()}_{platform.lower()}",
                    "password",
                ]
            ),
            "/".join(
                [
                    prefix,
                    f"{manufacturer.lower()}_{platform.lower()}",
                    "secret",
                ]
            ),
            "/".join(
                [
                    prefix,
                    f"{manufacturer.lower()}_{platform.lower()}",
                    "key",
                ]
            ),
        ]

    @staticmethod
    def lookup_nested_dict(param_list, key, value):
        """Lookup a value in a list of nested dicts."""
        for param in param_list:
            if value in param[key]:
                return param
        return {}

    def get_default_creds(self):
        """Get default credentials from environment variables.
        Returns:
            (tuple): Tuple of username, password, secret, key
        """
        prefix = "/netbox"
        parameter_names = [
            "/".join([prefix, "device_default", "username"]),
            "/".join([prefix, "device_default", "password"]),
            "/".join([prefix, "device_default", "secret"]),
            "/".join([prefix, "device_default", "key"]),
        ]
        return self.client.get_parameters(Names=parameter_names, WithDecryption=True)["Parameters"]

    def get_device_creds(self, device, **kwargs):
        """Get device credentials.

        Args:
            device (Device): NetBox device
            **kwargs: Additional arguments
        Returns:
            (tuple): Tuple of username, password, secret, key
        """
        if isinstance(device, Device):
            device_name = device.name
            manufacturer = device.device_type.manufacturer.slug
            platform = device.platform.slug
        else:
            device_name = device["name"]
            manufacturer = kwargs.get("manufacturer")
            platform = kwargs.get("platform")
        parameter_names = self.build_parameter_names(device_name, manufacturer, platform)
        credentials = self.client.get_parameters(Names=parameter_names, WithDecryption=True)["Parameters"]
        if not credentials:
            credentials = self.get_default_creds()
        return (
            self.lookup_nested_dict(credentials, "Name", "username").get("Value"),
            self.lookup_nested_dict(credentials, "Name", "password").get("Value"),
            self.lookup_nested_dict(credentials, "Name", "secret").get("Value"),
            self.lookup_nested_dict(credentials, "Name", "key").get("Value"),
        )
