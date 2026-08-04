from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from plugins.module_utils import config_loader
from plugins.module_utils.config_loader import ConfigLoader


class TestConfigLoaderMissingJsonschema:
    """
    Bug 3 regression tests: jsonschema/PyYAML should only be required when a
    config_file is actually supplied, not unconditionally on __init__.
    """

    def test_init_without_config_file_succeeds_when_jsonschema_missing(self, monkeypatch):
        monkeypatch.setattr(config_loader, 'JSONSCHEMA_IMPORT_ERROR', ImportError('no module named jsonschema'))

        loader = ConfigLoader(config_file=None)

        assert isinstance(loader, ConfigLoader)

    def test_init_without_config_file_succeeds_when_pyyaml_missing(self, monkeypatch):
        monkeypatch.setattr(config_loader, 'PYYAML_IMPORT_ERROR', ImportError('no module named yaml'))

        loader = ConfigLoader(config_file=None)

        assert isinstance(loader, ConfigLoader)

    def test_init_with_config_file_still_raises_when_jsonschema_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config_loader, 'JSONSCHEMA_IMPORT_ERROR', ImportError('no module named jsonschema'))
        config_file = tmp_path / "client.yaml"
        config_file.write_text("authentication:\n  access-token: abc\nservice:\n  server: https://example.com\n")

        with pytest.raises(ImportError, match="no module named jsonschema"):
            ConfigLoader(config_file=str(config_file))

    def test_init_with_config_file_still_raises_when_pyyaml_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config_loader, 'PYYAML_IMPORT_ERROR', ImportError('no module named yaml'))
        config_file = tmp_path / "client.yaml"
        config_file.write_text("authentication:\n  access-token: abc\nservice:\n  server: https://example.com\n")

        with pytest.raises(ImportError, match="no module named yaml"):
            ConfigLoader(config_file=str(config_file))


class TestConfigLoaderParsing:
    """Sanity checks that normal config file parsing still works when dependencies are present."""

    def test_parses_token_host_and_organization(self, tmp_path):
        config_file = tmp_path / "client.yaml"
        config_file.write_text(
            "organization: my-org\n"
            "authentication:\n"
            "  access-token: my-access-token\n"
            "service:\n"
            "  server: https://flightctl.example.com\n"
            "  insecureSkipVerify: true\n"
        )

        loader = ConfigLoader(config_file=str(config_file))

        assert loader.token == "my-access-token"
        assert loader.organization == "my-org"
        assert loader.host == "https://flightctl.example.com"
        assert loader.verify_ssl is False

    def test_missing_config_file_raises_clear_error(self, tmp_path):
        missing_path = tmp_path / "does_not_exist.yaml"

        with pytest.raises(Exception, match="was not found"):
            ConfigLoader(config_file=str(missing_path))
