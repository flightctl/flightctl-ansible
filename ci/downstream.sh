#!/usr/bin/env bash
set -e

# Get the desired version from a third argument, or default to a fixed version
DESIRED_VERSION="${1:-1.1.0}" 

# Output directory for the built collection artifact
_tmp_dir=$(mktemp -d)
OUTPUT_DIR="${_tmp_dir}/ansible_collections/redhat/edge_manager"

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLLECTION_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ABSOLUTE_COLLECTION_DIR="${2:-$COLLECTION_ROOT}"

GALAXY_YML_PATH="$ABSOLUTE_COLLECTION_DIR/galaxy.yml"
echo "Updating version in $GALAXY_YML_PATH to $DESIRED_VERSION..."
sed -i "s/^version: .*/version: $DESIRED_VERSION/" "$GALAXY_YML_PATH"

mkdir -p "$OUTPUT_DIR"
ansible-galaxy collection build "$ABSOLUTE_COLLECTION_DIR" --output-path "$OUTPUT_DIR"
echo "Collection build complete. Artifact(s) in $OUTPUT_DIR:"

ls -lh "$OUTPUT_DIR"/*.tar.gz
echo "Done."