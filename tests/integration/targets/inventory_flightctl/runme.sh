#!/usr/bin/env bash

set -eux

CMD_ARGS=("$@")

echo "Running inventory test with args: ${CMD_ARGS[*]}"

# Parse flightctl_host from the integration_config.yml file and pass it to the playbook
FLIGHTCTL_HOST=$(grep -oP 'flightctl_host:\s*\K.*' "../../integration_config.yml")
FLIGHTCTL_TOKEN=$(grep -oP 'flightctl_token:\s*\K.*' "../../integration_config.yml")

# Create inventory config directory
mkdir -p .config/flightctl

# Create inventory configuration file with comprehensive additional groups for testing
cat > .config/flightctl/inventory.yml <<EOF
---
plugin: flightctl.core.flightctl
verify_ssl: False
host: ${FLIGHTCTL_HOST}
token: ${FLIGHTCTL_TOKEN}
request_timeout: 120
additional_groups:
  # Group devices by machine type
  - name: forklift_machines
    label_selectors:
      - machine_type = forklift
  
  # Group devices by architecture
  - name: amd64_devices
    label_selectors:
      - arch = amd64
  
  - name: arm64_devices
    label_selectors:
      - arch = arm64
  
  # Group devices by location
  - name: lab_devices
    label_selectors:
      - location = lab
  
  # Group devices by fleet using field selectors
  - name: fleet_dev_devices
    field_selectors:
      - metadata.owner = "Fleet/fleet-dev"
  
  - name: fleet_test_devices
    field_selectors:
      - metadata.owner = "Fleet/fleet-test"
  
  - name: fleet_prod_devices
    field_selectors:
      - metadata.owner = "Fleet/fleet-prod"
  
  - name: integration_test_fleet_devices
    field_selectors:
      - metadata.owner = "Fleet/ansible-integration-test-fleet"
  
  # Test-specific groups using different selector combinations
  - name: test_group
    field_selectors:
      - metadata.name = 'ansible-integration-test-device'
  
  - name: integration_test_devices
    field_selectors:
      - metadata.name in ('ansible-integration-test-device', 'ansible-integration-test-device-label-1', 'ansible-integration-test-device-label-2')
  
  # Mixed selector groups
  - name: dev_amd64_devices
    label_selectors:
      - fleet = fleet-dev
      - arch = amd64
  
  - name: forklift_devices_by_name
    label_selectors:
      - machine_type = forklift
    field_selectors:
      - metadata.name in ('ansible-integration-test-device-label-1', 'ansible-integration-test-device-label-2')
EOF

echo "Step 1: Testing inventory plugin documentation..."
ansible-playbook ./inventory_doc_test.yml "${CMD_ARGS[@]}"

echo "Step 2: Setting up test resources..."
ansible-playbook ./inventory_setup_test.yml -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}"

# Wait a bit for resources to be fully created
echo "Waiting for resources to be ready..."
sleep 5

echo "Step 3: Testing inventory discovery..."
ansible-playbook ./inventory_test.yml -i ./.config/flightctl/inventory.yml -e "flightctl_host=${FLIGHTCTL_HOST}" -e "flightctl_token=${FLIGHTCTL_TOKEN}" "${CMD_ARGS[@]}"

echo "DONE"