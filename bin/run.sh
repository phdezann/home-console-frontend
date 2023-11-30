#!/usr/bin/env bash

set -e -u -x

python3 main.py \
  --mqtt-server="${MQTT_HOSTNAME}" "$@"
