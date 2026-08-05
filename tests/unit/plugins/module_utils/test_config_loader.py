from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os
from unittest import mock

import pytest

from plugins.module_utils.config_loader import ConfigLoader

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestConfigLoaderNoConfigFile:
    """ConfigLoader must succeed without jsonschema/pyyaml when config_file=None."""

    def test_init_without_config_file(self):
        loader = ConfigLoader(config_file=None)
        assert loader is not None

    def test_init_without_config_file_no_jsonschema(self):
        with mock.patch.dict(
            "plugins.module_utils.config_loader.__dict__",
            {"JSONSCHEMA_IMPORT_ERROR": ImportError("No module named 'jsonschema'")},
        ):
            loader = ConfigLoader(config_file=None)
            assert loader is not None

    def test_init_without_config_file_no_pyyaml(self):
        with mock.patch.dict(
            "plugins.module_utils.config_loader.__dict__",
            {"PYYAML_IMPORT_ERROR": ImportError("No module named 'yaml'")},
        ):
            loader = ConfigLoader(config_file=None)
            assert loader is not None

    def test_init_without_config_file_no_both(self):
        with mock.patch.dict(
            "plugins.module_utils.config_loader.__dict__",
            {
                "JSONSCHEMA_IMPORT_ERROR": ImportError("No module named 'jsonschema'"),
                "PYYAML_IMPORT_ERROR": ImportError("No module named 'yaml'"),
            },
        ):
            loader = ConfigLoader(config_file=None)
            assert loader is not None


class TestConfigLoaderMissingDependencies:
    """ConfigLoader must raise actionable ImportError when config_file is set but deps are missing."""

    def test_missing_jsonschema_raises_actionable_error(self):
        with mock.patch.dict(
            "plugins.module_utils.config_loader.__dict__",
            {"JSONSCHEMA_IMPORT_ERROR": ImportError("No module named 'jsonschema'")},
        ), pytest.raises(ImportError, match="pip install jsonschema"):
            ConfigLoader(config_file="some/path.yaml")

    def test_missing_pyyaml_raises_actionable_error(self):
        with mock.patch.dict(
            "plugins.module_utils.config_loader.__dict__",
            {"PYYAML_IMPORT_ERROR": ImportError("No module named 'yaml'")},
        ), pytest.raises(ImportError, match="pip install pyyaml"):
            ConfigLoader(config_file="some/path.yaml")

    def test_missing_pyyaml_checked_before_jsonschema(self):
        with mock.patch.dict(
            "plugins.module_utils.config_loader.__dict__",
            {
                "JSONSCHEMA_IMPORT_ERROR": ImportError("No module named 'jsonschema'"),
                "PYYAML_IMPORT_ERROR": ImportError("No module named 'yaml'"),
            },
        ), pytest.raises(ImportError, match="pip install pyyaml"):
            ConfigLoader(config_file="some/path.yaml")


class TestConfigLoaderWithConfigFile:
    """ConfigLoader correctly loads and parses valid config files."""

    def test_load_valid_config_file(self):
        config_file = os.path.join(FIXTURES_DIR, "client.yaml")
        loader = ConfigLoader(config_file=config_file)
        assert loader.host == "https://agent-api.flightctl.127.0.0.1.nip.io:7443"
        assert loader.organization == "00000000-0000-0000-0000-000000000000"

    def test_load_config_with_ca_data(self):
        config_file = os.path.join(FIXTURES_DIR, "client_with_ca_data.yaml")
        loader = ConfigLoader(config_file=config_file)
        assert loader.host == "https://192.168.86.25.nip.io:3443"
        assert hasattr(loader, "ca_data")

    def test_load_nonexistent_file_raises(self):
        with pytest.raises(Exception, match="was not found"):
            ConfigLoader(config_file="/nonexistent/path.yaml")

    def test_warn_callback_called(self):
        warnings = []
        config_file = os.path.join(FIXTURES_DIR, "client.yaml")
        ConfigLoader(config_file=config_file, warn_callback=warnings.append)
        # No warnings expected for a valid config with empty auth
        # Just verify the callback was accepted without error
