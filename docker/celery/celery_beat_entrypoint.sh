#!/bin/bash

set -o errexit
set -o nounset

rm -f './celerybeat.pid'
cd /opt/netbox/netbox
celery -A netbox_celery beat -l INFO -S netbox_celery.schedule.NetboxCeleryDatabaseScheduler
