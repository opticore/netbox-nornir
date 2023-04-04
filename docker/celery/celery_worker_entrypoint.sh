#!/bin/bash

set -o errexit
set -o nounset

cd /opt/netbox/netbox
celery -A netbox_celery worker -l INFO
