"""Default collection of Nornir Tasks based on Napalm."""
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
from nornir.core.exceptions import NornirSubTaskError
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command
from nornir_napalm.plugins.tasks import napalm_get

from netbox_nornir.exceptions import NornirNetboxException


RUN_COMMAND_MAPPING = {
    "default": "show run",
    "arista_eos": "show run",
    "cisco_aireos": "show run-config commands",
    "cisco_nxos": "show run",
    "cisco_ios": "show run",
    "cisco_wlc": "show running-config",
    "cisco_xr": "show run",
    "juniper_junos": "show configuration | display set",
    "netscaler": "show run",
}


class NetboxNornirDriver:
    """Default collection of Nornir Tasks based on Napalm."""

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
        logger.log_debug(
            f"Executing get_config for {task.host.name} on {task.host.platform}",
            grouping=task.host.name,
        )

        # TODO: Find standard napalm exceptions and account for them
        try:
            result = task.run(task=napalm_get, getters=["config"], retrieve="running")
        except NornirSubTaskError as exc:
            traceback_lines = exc.result[0].result.splitlines()
            logger.log_failure(
                obj,
                f"`get_config` method failed with an unexpected issue: `{traceback_lines[-1]}`",
                grouping=task.host.name,
            )
            for traceback_line in traceback_lines:
                logger.log_debug(
                    traceback_line,
                    grouping=task.host.name,
                )
            raise NornirNetboxException(
                f"`get_config` method failed with an unexpected issue: `{traceback_lines[-1]}`"
            ) from exc

        if result[0].failed:
            logger.log_failure(
                obj,
                f"`get_config` nornir task failed with an unexpected issue: `{str(result.exception)}`",
                grouping=task.host.name,
            )
            return result

        running_config = result[0].result.get("config", {}).get("running", None)
        return Result(host=task.host, result={"config": running_config})

    @staticmethod
    def naplam_get(task: Task, method, logger, obj) -> Result:
        """Get the latest facts from the device.
        Args:
            task (Task): Nornir Task.
            logger (NornirLogger): Custom NornirLogger object to reflect job results (via Netbox Jobs) and Python logger.
            obj (Device): A Netbox Device Django ORM object instance.
        Returns:
            Result: Nornir Result object with a dict as a result containing the method
                { "method: <method> }
        """
        logger.log_debug(
            f"Executing get_{method} for {task.host.name} on {task.host.platform}",
            grouping=task.host.name,
        )
        try:
            results = task.run(task=napalm_get, getters=[method])
        except NornirSubTaskError as exc:
            traceback_lines = exc.result[0].result.splitlines()
            logger.log_failure(
                obj,
                f"`get_{method}` method failed with an unexpected issue: `{traceback_lines[-1]}`",
                grouping=task.host.name,
            )
            for traceback_line in traceback_lines:
                logger.log_debug(
                    traceback_line,
                    grouping=task.host.name,
                )
            raise NornirNetboxException(
                f"`get_{method}` method failed with an unexpected issue: `{traceback_lines[-1]}`"
            ) from exc
        facts = results[0].result.get("facts", None)
        return Result(host=task.host, result={method: facts})

    @staticmethod
    def get_facts(task: Task, logger, obj) -> Result:
        return NetboxNornirDriver.naplam_get(task, "facts", logger, obj)

    @staticmethod
    def get_environment(task: Task, logger, obj) -> Result:
        return NetboxNornirDriver.naplam_get(task, "environment", logger, obj)

    @staticmethod
    def get_interfaces(task: Task, logger, obj) -> Result:
        """Get the latest interface IP addresses from the device.
        Args:
            task (Task): Nornir Task.
            logger (NornirLogger): Custom NornirLogger object to reflect job results (via Netbox Jobs) and Python logger.
            obj (Device): A Netbox Device Django ORM object instance.
        Returns:
            Result: Nornir Result object with a dict as a result containing the interface IP addresses
                { "interface_ip_addresses: <interface_ip_addresses> }
        """
        logger.log_debug(
            f"Executing get_interface_ip_addresses for {task.host.name} on {task.host.platform}",
            grouping=task.host.name,
        )
        try:
            results = task.run(task=napalm_get, getters=["interfaces", "interfaces_ip"])
        except NornirSubTaskError as exc:
            traceback_lines = exc.result[0].result.splitlines()
            logger.log_failure(
                obj,
                f"`get_interface_ip_addresses` method failed with an unexpected issue: `{traceback_lines[-1]}`",
                grouping=task.host.name,
            )
            for traceback_line in traceback_lines:
                logger.log_debug(
                    traceback_line,
                    grouping=task.host.name,
                )
            raise NornirNetboxException(
                f"`get_interface_ip_addresses` method failed with an unexpected issue: `{traceback_lines[-1]}`"
            ) from exc

        naplam_interfaces = results[0].result
        combined_interfaces = {}
        for interface_name, interface_details in naplam_interfaces["interfaces"].items():
            combined_interfaces[interface_name] = {
                **interface_details,
                **naplam_interfaces["interfaces_ip"].get(interface_name, {}),
            }
        return Result(host=task.host, result={"interfaces": combined_interfaces})


class NetmikoNetboxNornirDriver(NetboxNornirDriver):
    """Default collection of Nornir Tasks based on Netmiko."""

    @staticmethod
    def get_config(task: Task, logger, obj) -> Result:
        """Get the latest configuration from the device using Netmiko.

        Args:
            task (Task): Nornir Task.
            logger (NornirLogger): Custom NornirLogger object to reflect job results (via Netbox Jobs) and Python logger.
            obj (Device): A Netbox Device Django ORM object instance.
            remove_lines (list): A list of regex lines to remove configurations.
            substitute_lines (list): A list of dictionaries with to remove and replace lines.

        Returns:
            Result: Nornir Result object with a dict as a result containing the running configuration
                { "config: <running configuration> }
        """
        logger.log_debug(
            f"Executing get_config for {task.host.name} on {task.host.platform}",
            grouping=task.host.name,
        )
        command = RUN_COMMAND_MAPPING.get(task.host.platform, RUN_COMMAND_MAPPING["default"])

        try:
            result = task.run(task=netmiko_send_command, command_string=command)
        except NornirSubTaskError as exc:
            if isinstance(exc.result.exception, NetmikoAuthenticationException):
                logger.log_failure(
                    obj,
                    f"Failed with an authentication issue: `{exc.result.exception}`",
                    grouping=task.host.name,
                )
                raise NornirNetboxException(f"Failed with an authentication issue: `{exc.result.exception}`") from exc

            if isinstance(exc.result.exception, NetmikoTimeoutException):
                logger.log_failure(
                    obj,
                    f"Failed with a timeout issue. `{exc.result.exception}`",
                    grouping=task.host.name,
                )
                raise NornirNetboxException(f"Failed with a timeout issue. `{exc.result.exception}`") from exc

            logger.log_failure(
                obj,
                f"Failed with an unknown issue. `{exc.result.exception}`",
                grouping=task.host.name,
            )
            raise NornirNetboxException(f"Failed with an unknown issue. `{exc.result.exception}`") from exc

        if result[0].failed:
            return result

        running_config = result[0].result

        # Primarily seen in Cisco devices.
        if "ERROR: % Invalid input detected at" in running_config:
            logger.log_failure(
                obj,
                "Discovered `ERROR: % Invalid input detected at` in the output",
                grouping=task.host.name,
            )
            raise NornirNetboxException("Discovered `ERROR: % Invalid input detected at` in the output")

        return Result(host=task.host, result={"config": running_config})

    @staticmethod
    def get_facts(task: Task, logger, obj) -> Result:
        """Get the latest facts from the device using Netmiko.

        For overriding this function, the return needs to match the following format:
            {
                'uptime': (int),
                'vendor': (str),
                'os_version': (str),
                'serial_number': (str),
                'model': (str),
                'hostname': (str),
                'fqdn': (str),
                'interface_list': (list[str]),
            }
        This should match napalm's return object. The function should also set `self.facts` to the return value.
        """
        return NotImplementedError("get_facts is not implemented for NetmikoNetboxNornirDriver")

    @staticmethod
    def get_interfaces(task: Task, logger, obj) -> Result:
        """Get the latest interface IP addresses from the device using Netmiko.

        For overriding this function, the return needs to match the following format:
            {
                '{interface_name}': {
                    'is_up': (bool),
                    'is_enabled': (bool),
                    'description': (str),
                    'last_flapped': (float),
                    'mac_address': (str),
                    'speed': (int),
                    'mtu': (int),
                    'ipv4': {
                        '{ipv4_address}': {
                            'prefix_length': (int),
                        },
                        ...
                    },
                },
                ...
            }
        This should match napalm's return object. The function should also set `self.interfaces` to the return value.
        """
        return NotImplementedError("get_interfaces is not implemented for NetmikoNetboxNornirDriver")
