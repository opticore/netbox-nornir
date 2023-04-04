"""Credentials Class designed to work with environment variables."""
import os
from .base import BaseCredentials

USERNAME_ENV_VAR_NAME = "NAPALM_USERNAME"  # nosec
PASSWORD_ENV_VAR_NAME = "NAPALM_PASSWORD"  # nosec
SECRET_ENV_VAR_NAME = "DEVICE_SECRET"  # nosec


class CredentialsEnvVars(BaseCredentials):
    """Credentials Class designed to work with Netbox ORM.
    This class is the default class that will return the same login and password
    for all devices based on the values of the environment variables
    """

    def __init__(self, params={}):  # pylint: disable=dangerous-default-value
        """Initialize Credentials Class designed to work with environment variables.

        Args:
            params ([dict], optional): Credentials Parameters
        """
        if not isinstance(params, dict):
            raise TypeError("params must be a dictionary")

        self.username = os.getenv(params.get("username", USERNAME_ENV_VAR_NAME))
        self.password = os.getenv(params.get("password", PASSWORD_ENV_VAR_NAME))
        self.secret = os.getenv(params.get("secret", SECRET_ENV_VAR_NAME))

        if not self.secret:
            self.secret = self.password
