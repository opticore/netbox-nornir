# Netbox Nornir Plugin

## Overview

The Netbox Celery plugin is a Netbox plugin to provide support for celery. This plugin can be used base for any automation tasks.

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
