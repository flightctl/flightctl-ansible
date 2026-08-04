from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.utils import set_module_args
from plugins.module_utils.exceptions import FlightctlApiException


@pytest.fixture
def ib_module():
    set_module_args(dict(
        flightctl_host='https://test-imagebuilder.com/',
        flightctl_token='test-token'
    ))
    with patch('plugins.module_utils.imagebuilder_module.ApiClient'), \
         patch('plugins.module_utils.imagebuilder_module.Configuration'):
        from plugins.module_utils.imagebuilder_module import FlightctlImageBuilderModule
        module = FlightctlImageBuilderModule(argument_spec={})
    return module


@pytest.fixture
def ib_module_user_pass():
    set_module_args(dict(
        flightctl_host='https://test-imagebuilder.com/',
        flightctl_username='admin',
        flightctl_password='secret'
    ))
    with patch('plugins.module_utils.imagebuilder_module.ApiClient'), \
         patch('plugins.module_utils.imagebuilder_module.Configuration'), \
         patch('plugins.module_utils.imagebuilder_module.oidc_password_grant', return_value=('oidc-bearer-token', None)):
        from plugins.module_utils.imagebuilder_module import FlightctlImageBuilderModule
        module = FlightctlImageBuilderModule(argument_spec={})
    return module


class TestAuthHeaders:
    def test_bearer_token(self, ib_module):
        assert ib_module.headers == {'Authorization': 'Bearer test-token'}

    def test_username_password_uses_oidc_bearer_token(self, ib_module_user_pass):
        """username/password must be exchanged for a Bearer token via OIDC, never sent as Basic auth."""
        assert ib_module_user_pass.headers == {'Authorization': 'Bearer oidc-bearer-token'}

    def test_username_password_performs_oidc_grant_with_module_connection_params(self):
        set_module_args(dict(
            flightctl_host='https://test-imagebuilder.com/',
            flightctl_username='admin',
            flightctl_password='secret',
            flightctl_validate_certs=False,
        ))
        with patch('plugins.module_utils.imagebuilder_module.ApiClient'), \
             patch('plugins.module_utils.imagebuilder_module.Configuration'), \
             patch(
                'plugins.module_utils.imagebuilder_module.oidc_password_grant',
                return_value=('oidc-bearer-token', None),
             ) as mock_grant:
            from plugins.module_utils.imagebuilder_module import FlightctlImageBuilderModule
            module = FlightctlImageBuilderModule(argument_spec={})

        mock_grant.assert_called_once_with(
            host=module.host,
            username='admin',
            password='secret',
            verify_ssl=False,
            ca_path=None,
            request_timeout=10,
        )

    def test_username_password_oidc_failure_fails_module(self):
        """A failed OIDC grant should fail the module with the upstream error detail."""
        set_module_args(dict(
            flightctl_host='https://test-imagebuilder.com/',
            flightctl_username='admin',
            flightctl_password='secret',
        ))
        from plugins.module_utils.imagebuilder_module import FlightctlImageBuilderModule
        with patch('plugins.module_utils.imagebuilder_module.ApiClient'), \
             patch('plugins.module_utils.imagebuilder_module.Configuration'), \
             patch(
                'plugins.module_utils.imagebuilder_module.oidc_password_grant',
                return_value=(None, 'the server has no OIDC-based authentication provider configured'),
             ), \
             patch.object(FlightctlImageBuilderModule, 'fail_json', side_effect=SystemExit(1)) as mock_fail:
            with pytest.raises(SystemExit):
                FlightctlImageBuilderModule(argument_spec={})

        assert 'no OIDC-based authentication provider configured' in mock_fail.call_args.kwargs['msg']

    def test_no_auth(self):
        set_module_args(dict(
            flightctl_host='https://test-imagebuilder.com/',
        ))
        with patch('plugins.module_utils.imagebuilder_module.ApiClient'), \
             patch('plugins.module_utils.imagebuilder_module.Configuration'):
            from plugins.module_utils.imagebuilder_module import FlightctlImageBuilderModule
            module = FlightctlImageBuilderModule(argument_spec={})
        assert module.headers is None


class TestImageBuildOperations:
    def test_get_image_build(self, ib_module):
        mock_api = MagicMock()
        mock_build = MagicMock()
        mock_api.get_image_build.return_value = mock_build
        ib_module._imagebuild_api = mock_api

        result = ib_module.get_image_build("test-build")
        mock_api.get_image_build.assert_called_once()
        assert result == mock_build

    def test_get_image_build_with_exports(self, ib_module):
        mock_api = MagicMock()
        mock_build = MagicMock()
        mock_api.get_image_build.return_value = mock_build
        ib_module._imagebuild_api = mock_api

        result = ib_module.get_image_build("test-build", with_exports=True)
        mock_api.get_image_build.assert_called_once()
        assert result == mock_build

    def test_get_image_build_not_found(self, ib_module):
        from flightctl.imagebuilder.exceptions import NotFoundException
        mock_api = MagicMock()
        mock_api.get_image_build.side_effect = NotFoundException()
        ib_module._imagebuild_api = mock_api

        result = ib_module.get_image_build("missing")
        assert result is None

    def test_get_image_build_api_error(self, ib_module):
        from flightctl.imagebuilder.exceptions import ApiException
        mock_api = MagicMock()
        mock_api.get_image_build.side_effect = ApiException("server error")
        ib_module._imagebuild_api = mock_api

        with pytest.raises(FlightctlApiException, match="Unable to get ImageBuild"):
            ib_module.get_image_build("test-build")

    def test_list_image_builds(self, ib_module):
        mock_api = MagicMock()
        mock_list = MagicMock()
        mock_api.list_image_builds.return_value = mock_list
        ib_module._imagebuild_api = mock_api

        result = ib_module.list_image_builds(label_selector="env=prod", limit=10)
        mock_api.list_image_builds.assert_called_once()
        assert result == mock_list

    def test_list_image_builds_api_error(self, ib_module):
        from flightctl.imagebuilder.exceptions import ApiException
        mock_api = MagicMock()
        mock_api.list_image_builds.side_effect = ApiException("server error")
        ib_module._imagebuild_api = mock_api

        with pytest.raises(FlightctlApiException, match="Unable to list ImageBuilds"):
            ib_module.list_image_builds()

    def test_create_image_build(self, ib_module):
        mock_api = MagicMock()
        mock_result = MagicMock()
        mock_api.create_image_build.return_value = mock_result
        ib_module._imagebuild_api = mock_api

        definition = {
            "apiVersion": "imagebuilder.flightctl.io/v1alpha1",
            "kind": "ImageBuild",
            "metadata": {"name": "test-build"},
            "spec": {},
        }

        with patch('plugins.module_utils.imagebuilder_module.ImageBuild') as mock_model:
            mock_obj = MagicMock()
            mock_model.from_dict.return_value = mock_obj
            result = ib_module.create_image_build(definition)

        mock_model.from_dict.assert_called_once_with(definition)
        assert result == mock_result

    def test_delete_image_build(self, ib_module):
        mock_api = MagicMock()
        ib_module._imagebuild_api = mock_api

        ib_module.delete_image_build("test-build")
        mock_api.delete_image_build.assert_called_once()

    def test_cancel_image_build(self, ib_module):
        mock_api = MagicMock()
        mock_result = MagicMock()
        mock_api.cancel_image_build.return_value = mock_result
        ib_module._imagebuild_api = mock_api

        result = ib_module.cancel_image_build("test-build")
        mock_api.cancel_image_build.assert_called_once()
        assert result == mock_result

    def test_get_image_build_log(self, ib_module):
        mock_api = MagicMock()
        mock_api.get_image_build_log.return_value = "build log output"
        ib_module._imagebuild_api = mock_api

        result = ib_module.get_image_build_log("test-build")
        mock_api.get_image_build_log.assert_called_once()
        assert result == "build log output"


class TestImageExportOperations:
    def test_get_image_export(self, ib_module):
        mock_api = MagicMock()
        mock_export = MagicMock()
        mock_api.get_image_export.return_value = mock_export
        ib_module._imageexport_api = mock_api

        result = ib_module.get_image_export("test-export")
        mock_api.get_image_export.assert_called_once()
        assert result == mock_export

    def test_get_image_export_not_found(self, ib_module):
        from flightctl.imagebuilder.exceptions import NotFoundException
        mock_api = MagicMock()
        mock_api.get_image_export.side_effect = NotFoundException()
        ib_module._imageexport_api = mock_api

        result = ib_module.get_image_export("missing")
        assert result is None

    def test_list_image_exports(self, ib_module):
        mock_api = MagicMock()
        mock_list = MagicMock()
        mock_api.list_image_exports.return_value = mock_list
        ib_module._imageexport_api = mock_api

        result = ib_module.list_image_exports(field_selector="status=Completed")
        mock_api.list_image_exports.assert_called_once()
        assert result == mock_list

    def test_create_image_export(self, ib_module):
        mock_api = MagicMock()
        mock_result = MagicMock()
        mock_api.create_image_export.return_value = mock_result
        ib_module._imageexport_api = mock_api

        definition = {
            "apiVersion": "imagebuilder.flightctl.io/v1alpha1",
            "kind": "ImageExport",
            "metadata": {"name": "test-export"},
            "spec": {},
        }

        with patch('plugins.module_utils.imagebuilder_module.ImageExport') as mock_model:
            mock_obj = MagicMock()
            mock_model.from_dict.return_value = mock_obj
            result = ib_module.create_image_export(definition)

        mock_model.from_dict.assert_called_once_with(definition)
        assert result == mock_result

    def test_delete_image_export(self, ib_module):
        mock_api = MagicMock()
        ib_module._imageexport_api = mock_api

        ib_module.delete_image_export("test-export")
        mock_api.delete_image_export.assert_called_once()

    def test_cancel_image_export(self, ib_module):
        mock_api = MagicMock()
        mock_result = MagicMock()
        mock_api.cancel_image_export.return_value = mock_result
        ib_module._imageexport_api = mock_api

        result = ib_module.cancel_image_export("test-export")
        mock_api.cancel_image_export.assert_called_once()
        assert result == mock_result

    def test_get_image_export_log(self, ib_module):
        mock_api = MagicMock()
        mock_api.get_image_export_log.return_value = "export log output"
        ib_module._imageexport_api = mock_api

        result = ib_module.get_image_export_log("test-export")
        mock_api.get_image_export_log.assert_called_once()
        assert result == "export log output"

    def test_download_image_export(self, ib_module):
        mock_api = MagicMock()
        mock_api.download_image_export.return_value = bytearray(b'\x00\x01\x02')
        ib_module._imageexport_api = mock_api

        result = ib_module.download_image_export("test-export")
        mock_api.download_image_export.assert_called_once()
        assert result == bytearray(b'\x00\x01\x02')

    def test_download_image_export_api_error(self, ib_module):
        from flightctl.imagebuilder.exceptions import ApiException
        mock_api = MagicMock()
        mock_api.download_image_export.side_effect = ApiException("download failed")
        ib_module._imageexport_api = mock_api

        with pytest.raises(FlightctlApiException, match="Unable to download ImageExport"):
            ib_module.download_image_export("test-export")
