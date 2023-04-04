"""Cisco IOS RESTCONF driver."""
import requests
from nornir.core.task import Result, Task

from .default import NetmikoNetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Fortigate for configuration backup."""

    @staticmethod
    def get_config(task: Task, logger, obj) -> Result:
        """Get the latest configuration from the device.
        Args:
            task (Task): Nornir Task.
            logger (NornirLogger): Custom NornirLogger object to reflect job results (via Netbox Jobs) and Python logger.
            obj (Device): A Netbox Device Django ORM object instance.
        Returns:
            Result: Nornir Result object with a dict as a result containing the running configuration
                { "config: <running configuration> }
        """

        session = requests.Session()
        session.trust_env = False
        logger.log_debug(
            f"Executing get_config for {task.host.name} on {task.host.platform}",
            grouping=task.host.name,
        )
        auth = (task.host.username, task.host.password)
        headers = {"Accept": "application/yang-data+json"}
        params = {"content": "config", "depth": "65535"}

        response = session.get(
            f"https://{task.host.hostname}/restconf/data/Cisco-IOS-XE-native:native",
            auth=auth,
            headers=headers,
            params=params,
            verify=False,
            timeout=10,
        )
        response.raise_for_status()
        return Result(host=task.host, result={"config": response.text})
