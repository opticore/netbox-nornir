# Nornir Inventory

Using the `NetboxORMInventory` class inside of your Nornir initiation will allow the user to create a inventory from the Netbox ORM.

## `NetboxORMInventory`

Arguments:

- `queryset` (`dcim.models.Device`): Queryset of devices to be loaded into inventory.
- `filters` (`dict`): A dictionary of filters to be used against the queryset.
- `credentials_class` (`str`): Import path to be used to load credentials per `Device` object.
- `credentials_params` (`dict`): Parameters to be used with the credentials class.

### Credentials Classes

Credentials classes can be dynamically imported from any Python path. This allows the user to create their own method to gather credentials from anywhere.

By default a basic credentials class is set (`CredentialsEnvVars`). For each host this class gets initiated.

``` python
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
        self.username = os.getenv(params.get("username", USERNAME_ENV_VAR_NAME))
        self.password = os.getenv(params.get("password", PASSWORD_ENV_VAR_NAME))
        self.secret = os.getenv(params.get("secret", SECRET_ENV_VAR_NAME))

        if not self.secret:
            self.secret = self.password
```

The example above shows the class getting initiated and setting three attributes to itself using environmental variables. The username, password and secret.
