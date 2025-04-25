#!/usr/bin/env bash

set -eux

CMD_ARGS=("$@")

echo "Running ansible-playbook with args: ${CMD_ARGS[*]}"

# Parse flightctl_host from the integration_config.yml file and pass it to the paybook
FLIGHTCTL_HOST=$(grep -oP 'flightctl_host:\s*\K.*' "../../integration_config.yml")
FLIGHTCTL_TOKEN=$(grep -oP 'flightctl_token:\s*\K.*' "../../integration_config.yml")

ansible-playbook "./test_connection.yml" -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}"

echo "DONE"
