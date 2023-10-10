"""Palo Alto PANOS driver."""
import xml.dom.minidom

import requests
from nornir.core.task import Result, Task

from .default import NetmikoNetboxNornirDriver as DefaultNetboxNornirDriver


class NetboxNornirDriver(DefaultNetboxNornirDriver):
    """Palo Alto PANOS driver for configuration backup."""

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
        if task.host.port == 22:
            port = 443
        else:
            port = task.host.port
        response = session.get(
            f"https://{task.host.hostname}:{port}/api/?type=export&category=configuration&key={task.host.data['key']}",
            verify=False,
            timeout=10,
        )
        response.raise_for_status()
        xml_response = xml.dom.minidom.parseString(response.text)
        xml_pretty = xml_response.toprettyxml()
        return Result(host=task.host, result={"config": xml_pretty})
