#!/usr/bin/env bash

set -euxo pipefail

CMD_ARGS=("$@")

echo "Running ansible-playbook with args: ${CMD_ARGS[*]}"

# Parse flightctl_host from the integration_config.yml file and pass it to the paybook
FLIGHTCTL_HOST=$(awk -F': ' '/^flightctl_host:/ {print $2}' "../../integration_config.yml")
FLIGHTCTL_TOKEN=$(awk -F': ' '/^flightctl_token:/ {print $2}' "../../integration_config.yml")

ansible-playbook "./inventory_doc_test.yml" -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}" -vvv
ansible-playbook "./inventory_test.yml" -i "./.config/flightctl/flightctl.inventory.yml" -e "flightctl_host=${FLIGHTCTL_HOST}"  -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}" -vvv
echo "DONE"
