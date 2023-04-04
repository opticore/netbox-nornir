"""Constants for plugin."""
from django.conf import settings


_NORNIR_SETTINGS = {
    "inventory": "netbox_nornir.plugins.inventory.netbox_orm.NetboxORMInventory",
    "credentials": "netbox_nornir.plugins.credentials.env_vars.CredentialsEnvVars",
    "runner": {"options": {"num_workers": 20}},
}

PLUGIN_CFG = settings.PLUGINS_CONFIG.get("netbox_nornir", {})
NORNIR_SETTINGS = PLUGIN_CFG.get("nornir_settings", _NORNIR_SETTINGS)
CONNECTION_SECRETS_PATHS = {
    "netmiko": "netmiko.extras.secret",
    "napalm": "napalm.extras.optional_args.secret",
    "scrapli": "scrapli.extras.auth_secondary",
}

CONNECTION_ENABLE_PASSWORD_PATHS = {
    "netmiko": "netmiko.extras.enable_password",
    "napalm": "napalm.extras.optional_args.enable_password",
    "scrapli": "scrapli.extras.enable_password",
}
