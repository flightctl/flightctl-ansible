#!/usr/bin/env bash
set -e

VERSION="${1:-1.2.0}"
COLLECTION_ROOT="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Create a temporary directory and a specific output path
_tmp_dir=$(mktemp -d)
trap 'rm -rf "$_tmp_dir"' EXIT
OUTPUT_DIR="${_tmp_dir}/ansible_collections"

# Copy the collection source into the temp dir (exclude VCS/build artifacts)
rsync -a --delete \
  --exclude '.git' \
  --exclude '.github' \
  --exclude 'build' \
  --exclude '.tox' \
  --exclude 'venv' \
  --exclude '.venv' \
  "${COLLECTION_ROOT}/" "${_tmp_dir}/"

# Override metadata for this build
sed "s/^version: .*/version: $VERSION/; s/^namespace: .*/namespace: redhat/; s/^name: .*/name: edge_manager/" "$COLLECTION_ROOT/galaxy.yml" > "$_tmp_dir/galaxy.yml"

# Build the collection from the temporary directory
mkdir -p "$OUTPUT_DIR"
command -v ansible-galaxy >/dev/null || { echo "ansible-galaxy not found in PATH" >&2; exit 1; }
ansible-galaxy collection build "$_tmp_dir" --output-path "$OUTPUT_DIR"