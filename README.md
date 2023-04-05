# Netbox Nornir Plugin

## Overview

The Netbox Nornir plugin is a shim layer for OpticoreIT netbox plugins. OpticoreIT use this plugin as a base for network automation solutions.

Main functions:

  1) Nornir inventory for Netbox ORM
  2) Generic credentials integrations
  3) Generic data collection from different device types

## Installation

1. Install the package using pip:

``` bash
pip install netbox-nornir
```

2. Add plugin to `PLUGINS` in configuration:

``` python
PLUGINS = [
    ...
    "netbox_nornir",
    ...
]
```
