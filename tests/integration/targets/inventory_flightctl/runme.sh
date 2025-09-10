#!/usr/bin/env bash

set -eux

CMD_ARGS=("$@")

echo "Running inventory test with args: ${CMD_ARGS[*]}"

# Parse flightctl_host from the integration_config.yml file and pass it to the playbook
FLIGHTCTL_HOST=$(grep -oP 'flightctl_host:\s*\K.*' "../../integration_config.yml")
FLIGHTCTL_TOKEN=$(grep -oP 'flightctl_token:\s*\K.*' "../../integration_config.yml")

# Create inventory config directory
mkdir -p .config/flightctl

# Create inventory configuration file
cat > .config/flightctl/inventory.yml <<EOF
---
plugin: flightctl.core.flightctl
flightctl_validate_certs: False
verify_ssl: False
flightctl_host: ${FLIGHTCTL_HOST}
flightctl_token: ${FLIGHTCTL_TOKEN}
request_timeout: 120
additional_groups:
  - name: test_group
    field_selectors:
      - metadata.name = 'ansible-integration-test-device'
EOF

ansible-playbook ./inventory_test.yml -i ./.config/flightctl/inventory.yml -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}"

echo "DONE"
