"""Used to intialize the dispatcher."""
# pylint: disable=raise-missing-from

import importlib
import logging

from nornir.core.exceptions import NornirSubTaskError
from nornir.core.task import Result, Task
from netbox_nornir.exceptions import NornirNetboxException


LOGGER = logging.getLogger(__name__)

_DEFAULT_DRIVERS_MAPPING = {
    "default": "netbox_nornir.plugins.tasks.dispatcher.default.NetboxNornirDriver",
    "default_netmiko": "netbox_nornir.plugins.tasks.dispatcher.default.NetmikoNetboxNornirDriver",
    "arista_eos": "netbox_nornir.plugins.tasks.dispatcher.arista_eos.NetboxNornirDriver",
    "cisco_aireos": "netbox_nornir.plugins.tasks.dispatcher.cisco_aireos.NetboxNornirDriver",
    "cisco_asa": "netbox_nornir.plugins.tasks.dispatcher.cisco_asa.NetboxNornirDriver",
    "cisco_ios": "netbox_nornir.plugins.tasks.dispatcher.cisco_ios.NetboxNornirDriver",
    "cisco_ios_restconf": "netbox_nornir.plugins.tasks.dispatcher.cisco_ios_restconf.NetboxNornirDriver",
    "cisco_nxos": "netbox_nornir.plugins.tasks.dispatcher.cisco_nxos.NetboxNornirDriver",
    "cisco_wlc": "netbox_nornir.plugins.tasks.dispatcher.cisco_wlc.NetboxNornirDriver",
    "cisco_xr": "netbox_nornir.plugins.tasks.dispatcher.cisco_ios_xr.NetboxNornirDriver",
    "fortinet_fortios": "netbox_nornir.plugins.tasks.dispatcher.fortinet_fortios.NetboxNornirDriver",
    "juniper_junos": "netbox_nornir.plugins.tasks.dispatcher.juniper_junos.NetboxNornirDriver",
    "netscaler": "netbox_nornir.plugins.tasks.dispatcher.netscaler.NetboxNornirDriver",
    "paloalto_panos": "netbox_nornir.plugins.tasks.dispatcher.paloalto_panos.NetboxNornirDriver",
}


def dispatcher(task: Task, method: str, logger, obj, *args, **kwargs) -> Result:
    """Helper Task to retrieve a given Nornir task for a given platform.

    Args:
        task (Nornir Task):  Nornir Task object.
        method (str):  The string value of the method to dynamically find.

    Returns:
        Result: Nornir Task result.
    """
    if kwargs.get("default_drivers_mapping"):
        default_drivers_mapping = kwargs["default_drivers_mapping"]
        del kwargs["default_drivers_mapping"]
    else:
        default_drivers_mapping = _DEFAULT_DRIVERS_MAPPING

    logger.log_debug(
        f"Executing dispatcher for {task.host.name} ({task.host.platform})",
        grouping=task.host.name,
    )

    # Get the platform specific driver, if not available, get the default driver
    driver = default_drivers_mapping.get(task.host.platform, default_drivers_mapping.get("default"))
    logger.log_debug(f"Found driver {driver}", grouping=task.host.name)

    if not driver:
        logger.log_failure(
            obj,
            f"Unable to find the driver for {method} for platform: {task.host.platform}, preemptively failed.",
            grouping=task.host.name,
        )
        raise NornirNetboxException(
            f"Unable to find the driver for {method} for platform: {task.host.platform}, preemptively failed."
        )

    module_name, class_name = driver.rsplit(".", 1)
    driver_class = getattr(importlib.import_module(module_name), class_name)

    if not driver_class:
        logger.log_failure(
            obj,
            f"Unable to locate the class {driver}, preemptively failed.",
            grouping=task.host.name,
        )
        raise NornirNetboxException(f"Unable to locate the class {driver}, preemptively failed.")

    try:
        driver_task = getattr(driver_class, method)
    except AttributeError:
        logger.log_failure(
            obj,
            f"Unable to locate the method {method} for {driver}, preemptively failed.",
            grouping=task.host.name,
        )
        raise NornirNetboxException(f"Unable to locate the method {method} for {driver}, preemptively failed.")

    result = None
    error = None
    try:
        result = task.run(task=driver_task, logger=logger, obj=obj, *args, **kwargs)
    except NornirSubTaskError as exc:
        traceback_lines = exc.result[0].result.splitlines()
        logger.log_failure(obj, f"Subtask failed: {traceback_lines[-1]}", grouping=task.host.name)
        error = traceback_lines[-1]
        for line in traceback_lines:
            logger.log_debug(line, grouping=task.host.name)
        raise NornirNetboxException(f"Subtask failed: {traceback_lines[-1]}")
    return Result(
        host=task.host,
        result=result,
        error=error,
    )
