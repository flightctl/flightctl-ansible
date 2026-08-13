#!/usr/bin/env bash

set -euo pipefail

CMD_ARGS=("$@")

echo "Running inventory test with args: ${CMD_ARGS[*]}"

# Parse credentials from integration_config.yml — suppress tracing to avoid exposing secrets in CI logs
{ set +x; } 2>/dev/null
FLIGHTCTL_HOST=$(grep -oP 'flightctl_host:\s*\K.*' "../../integration_config.yml")
FLIGHTCTL_TOKEN=$(grep -oP 'flightctl_token:\s*\K.*' "../../integration_config.yml")
FLIGHTCTL_ORGANIZATION="$(grep -oP 'flightctl_organization:\s*\K.*' "../../integration_config.yml" || true)"
export FLIGHTCTL_HOST FLIGHTCTL_TOKEN FLIGHTCTL_ORGANIZATION
# Write credentials to a restricted temp vars file so they do not appear in
# the process argument list of ansible-playbook calls.
if [[ -z "${FLIGHTCTL_HOST}" || -z "${FLIGHTCTL_TOKEN}" ]]; then
  printf 'error: flightctl_host and flightctl_token are required in integration_config.yml\n' >&2
  exit 1
fi
VARS_FILE=$(mktemp)
# Register cleanup immediately after mktemp — before chmod/printf — so the
# file is removed even if a subsequent command fails under set -e.
cleanup() {
  ansible-playbook ./inventory_cleanup_test.yml -e "@${VARS_FILE}" "${CMD_ARGS[@]}" 2>/dev/null || true
  rm -f "${VARS_FILE}" ".config/flightctl/inventory.yml" ".config/flightctl/env_only.inventory.yml"
}
trap cleanup EXIT
chmod 600 "${VARS_FILE}"
printf 'flightctl_host: "%s"\nflightctl_token: "%s"\nflightctl_organization: "%s"\n' \
  "${FLIGHTCTL_HOST}" "${FLIGHTCTL_TOKEN}" "${FLIGHTCTL_ORGANIZATION}" > "${VARS_FILE}"
set -x

# Create inventory config directory
mkdir -p .config/flightctl

# Create inventory configuration file — suppress tracing while credentials are expanded
{ set +x; } 2>/dev/null
cat > .config/flightctl/inventory.yml <<EOF
---
plugin: flightctl.core.flightctl
verify_ssl: False
host: ${FLIGHTCTL_HOST}
token: ${FLIGHTCTL_TOKEN}
organization: ${FLIGHTCTL_ORGANIZATION}
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
set -x

echo "Step 1: Testing inventory plugin documentation..."
ansible-playbook ./inventory_doc_test.yml "${CMD_ARGS[@]}"

echo "Step 2: Setting up test resources..."
ansible-playbook ./inventory_setup_test.yml -e "@${VARS_FILE}" "${CMD_ARGS[@]}"

# Wait a bit for resources to be fully created
echo "Waiting for resources to be ready..."
sleep 5

echo "Step 3: Testing inventory discovery..."
ansible-playbook ./inventory_test.yml -i ./.config/flightctl/inventory.yml -e "@${VARS_FILE}" "${CMD_ARGS[@]}"

# Write a credential-free inventory file — host/token/org must come from env vars.
# This simulates how AAP injects credentials via a Credential Type (EDM-4975).
cat > .config/flightctl/env_only.inventory.yml <<EOF
---
plugin: flightctl.core.flightctl
verify_ssl: False
EOF

echo "Step 4: Testing env var credential injection (AAP Credential Type simulation / EDM-4975)..."
ansible-playbook ./inventory_env_vars_test.yml -e "@${VARS_FILE}" "${CMD_ARGS[@]}"

echo "DONE"
