#!/usr/bin/env bash
set -e

DESIRED_VERSION="${1:-1.2.0}"
COLLECTION_ROOT="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
GALAXY_YML="$COLLECTION_ROOT/galaxy.yml"

# Create a temporary directory and a specific output path
_tmp_dir=$(mktemp -d)
OUTPUT_DIR="${_tmp_dir}/ansible_collections/redhat/edge_manager"
mkdir -p "$OUTPUT_DIR"

# Cleanup - restoring the galaxy.yml and removing the temp directory
trap 'mv "$GALAXY_YML.backup" "$GALAXY_YML" && rm -rf "$_tmp_dir"' EXIT

# Backup galaxy.yml and modify it
cp "$GALAXY_YML" "$GALAXY_YML.backup"
sed -i "s/^version: .*/version: $DESIRED_VERSION/; s/^namespace: .*/namespace: redhat/; s/^name: .*/name: edge_manager/" "$GALAXY_YML"

# Build the collection
ansible-galaxy collection build "$COLLECTION_ROOT" --output-path "$OUTPUT_DIR"