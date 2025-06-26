#!/usr/bin/env bash

set -euxo pipefail

CMD_ARGS=("$@")

echo "Running ansible-playbook with args: ${CMD_ARGS[*]}"

# Parse flightctl_host from the integration_config.yml file and pass it to the paybook
FLIGHTCTL_HOST=$(grep -oP 'flightctl_host:\s*\K.*' "../../integration_config.yml")
FLIGHTCTL_TOKEN=$(grep -oP 'flightctl_token:\s*\K.*' "../../integration_config.yml")

# Pass integration configuration directly; avoids fragile parsing and leaking secrets
ansible-playbook "./inventory_doc_test.yml" -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}" -vvv
ansible-playbook "./inventory_setup_test.yml" -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}" -vvv

ansible-playbook "./inventory_test.yml" -i "./.config/flightctl/flightctl.inventory.yaml" -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}" -vvv

echo "DONE"
