# Netbox Nornir Plugin

<p align="center">
  <img src="https://raw.githubusercontent.com/opticore/netbox-nornir/main/docs/assets/netbox_nornir.png" class="logo" height="200px">
  <br>
  <a href="https://github.com/opticore/netbox-nornir/actions"><img src="https://github.com/opticore/netbox-nornir/actions/workflows/ci_integration.yml/badge.svg?branch=main"></a>
  <a href="https://pypi.org/project/netbox-nornir/"><img src="https://img.shields.io/pypi/v/netbox-nornir"></a>
  <a href="https://pypi.org/project/netbox-nornir/"><img src="https://img.shields.io/pypi/dm/netbox-nornir"></a>
  <br>
  An App for <a href="https://github.com/netbox-community/netbox">Netbox</a>.
</p>

## Overview

The Netbox Nornir plugin is a shim layer for OpticoreIT netbox plugins. OpticoreIT use this plugin as a base for network automation solutions. The plugin is based on a [nautobot-nornir](https://github.com/nautobot/nautobot-plugin-nornir) created by NTC.

Main functions:

  1. Nornir inventory for Netbox ORM
  2. Generic credentials integrations
  3. Generic data collection from different device types

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
