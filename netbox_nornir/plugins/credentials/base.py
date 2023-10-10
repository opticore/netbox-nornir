"""Base credentials plugin for Netbox Nornir."""


class BaseCredentials:
    """Base credentials plugin for Netbox Nornir."""

    username = None
    password = None
    secret = None
    key = None

    def get_device_creds(self, device=None):  # pylint: disable=unused-argument
        """Return the credentials for a given device.
        Args:
            device (dcim.models.Device): Netbox device object
        Return:
            username (string):
            password (string):
            secret (string):
        """

        return (self.username, self.password, self.secret, self.key)
