#!/bin/bash -eu

# Script to dual-home the upstream and downstream Collection in a single repo
#
#   This script will build or test a downstream collection, removing any
#   upstream components that will not ship in the downstream release
#
#   NOTES:
#       - All functions are prefixed with f_ so it's obvious where they come
#         from when in use throughout the script

DOWNSTREAM_VERSION="1.0.0"
KEEP_DOWNSTREAM_TMPDIR="${KEEP_DOWNSTREAM_TMPDIR:-''}"
INSTALL_DOWNSTREAM_COLLECTION_PATH="${INSTALL_DOWNSTREAM_COLLECTION_PATH:-}"
_build_dir=""

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."

f_log_info()
{
    printf "%s:LOG:INFO: %s\n" "${0}" "${1}"
}

f_show_help()
{
    printf "Usage: downstream.sh [OPTION]\n"
    printf "\t-s\t\tCreate a temporary downstream release and perform sanity tests.\n"
    printf "\t-u\t\tCreate a temporary downstream release and perform unit tests.\n"
    printf "\t-i\t\tCreate a temporary downstream release and perform integration tests.\n"
    printf "\t-b\t\tBuild the downstream release.\n"
}

f_text_sub()
{
    f_log_info "Substituting text in files"

    find "${_build_dir}" -type f -exec sed -i.bak "s/flightctl\.core/redhat.edge_manager/g" {} \;

    sed -i.bak "s/Flight Control Collection/Red Hat Edge Manager Collection/g" "${_build_dir}/README.md"
    sed -i.bak "s/flightctl\/core/redhat\/edge_manager/g" "${_build_dir}/galaxy.yml"
    sed -i.bak "s/flightctl\/core/redhat\/edge_manager/g" "${_build_dir}/README.md"
    sed -i.bak "s/^version\:.*$/version: ${DOWNSTREAM_VERSION}/" "${_build_dir}/galaxy.yml"
    sed -i.bak "s/^namespace\:.*$/namespace: redhat/" "${_build_dir}/galaxy.yml"
    sed -i.bak "s/^name\:.*$/name: edge_manager/" "${_build_dir}/galaxy.yml"
    sed -i.bak "s/core/edge_manager/g" "${_build_dir}/meta/runtime.yml"

    find "${_build_dir}" -type f -name "*.bak" -delete
}

f_prep()
{
    f_log_info "Creating temporary build directory"
    # Array of excluded files from downstream build (relative path)
    _file_exclude=(
    )

    # Files to copy downstream (relative repo root dir path)
    _file_manifest=(
        CHANGELOG.rst
        galaxy.yml
        LICENSE
        README.md
        Makefile
        requirements.txt
    )

    # Directories to recursively copy downstream (relative repo root dir path)
    _dir_manifest=(
        changelogs
        meta
        plugins
        tests
    )

    # Temp build dir
    _tmp_dir=$(mktemp -d)
    _build_dir="${_tmp_dir}/ansible_collections/redhat/edge_manager"
    mkdir -p "${_build_dir}"
}

f_cleanup()
{
    f_log_info "Cleaning up"
    if [[ -n "${_build_dir}" ]]; then
        if [[ -z ${KEEP_DOWNSTREAM_TMPDIR} ]]; then
            if [[ -d ${_build_dir} ]]; then
                rm -fr "${_build_dir}"
            fi
        fi
    fi
}

# Exit and handle cleanup processes if needed
trap f_cleanup EXIT

f_exit()
{
    f_cleanup
    exit "$0"
}

f_create_collection_dir_structure()
{
    f_log_info "Creating collection directory structure"
    # Create the Collection
    for f_name in "${_file_manifest[@]}";
    do
        cp "${ROOT_DIR}/${f_name}" "${_build_dir}/${f_name}"
    done
    for d_name in "${_dir_manifest[@]}";
    do
        cp -r "${ROOT_DIR}/${d_name}" "${_build_dir}/${d_name}"
    done
    if [ -n "${_file_exclude:-}" ]; then
        for exclude_file in "${_file_exclude[@]}";
        do
            if [[ -f "${_build_dir}/${exclude_file}" ]]; then
                rm -f "${_build_dir}/${exclude_file}"
            fi
        done
    fi
}

f_copy_collection_to_working_dir()
{
    f_log_info "Copying built collection to working dir"
    # Copy the Collection build result into original working dir
    f_log_info "Copying built collection *.tar.gz into ./"
    cp "${_build_dir}"/*.tar.gz "${ROOT_DIR}/"
    # Install downstream collection into provided path
    if [[ -n ${INSTALL_DOWNSTREAM_COLLECTION_PATH} ]]; then
        f_log_info "Installing built collection *.tar.gz into ${INSTALL_DOWNSTREAM_COLLECTION_PATH}"
        ansible-galaxy collection install -p "${INSTALL_DOWNSTREAM_COLLECTION_PATH}" "${_build_dir}"/*.tar.gz
    fi
    rm -f "${_build_dir}"/*.tar.gz
}

f_common_steps()
{
    f_prep
    f_create_collection_dir_structure
    f_text_sub
}

# Run the test sanity scenario
f_test_sanity_option()
{
    f_log_info "Running Sanity Tests"
    f_common_steps
    pushd "${_build_dir}" || return
        make sanity-test
    popd || return
    f_cleanup
}

# Run the test integration
f_test_integration_option()
{
    f_log_info "Running Integration Tests"
    f_common_steps
    pushd "${_build_dir}" || return
        make integration-test
    popd || return
    f_cleanup
}

# Run the test units
f_test_units_option()
{
    f_log_info "Running Unit Tests"
    f_common_steps
    pushd "${_build_dir}" || return
        make unit-test
    popd || return
    f_cleanup
}

# Run the build scenario
f_build_option()
{
    f_log_info "Building Collection"
    f_common_steps
    pushd "${_build_dir}" || return
        ansible-galaxy collection build
    popd || return
    f_copy_collection_to_working_dir
    f_cleanup
}

# If no options are passed, display usage and exit
if [[ "${#}" -eq "0" ]]; then
    f_show_help
    f_exit 0
fi

# Handle options
while getopts ":siub" option
do
  case $option in
    s)
        f_test_sanity_option
        ;;
    i)
        f_test_integration_option
        ;;
    u)
        f_test_units_option
        ;;
    b)
        f_build_option
        ;;
    *)
        printf "ERROR: Unimplemented option chosen.\n"
        f_show_help
        f_exit 1
        ;;
  esac
done