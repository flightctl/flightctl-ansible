from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from tests.unit.utils import set_module_args


IB_MODULE_PATH = 'plugins.module_utils.imagebuilder_module'
IB_CLASS = f'{IB_MODULE_PATH}.FlightctlImageBuilderModule'


@pytest.fixture(autouse=True)
def _patch_ib_client():
    with patch(f'{IB_MODULE_PATH}.ApiClient'), \
         patch(f'{IB_MODULE_PATH}.Configuration'):
        yield


class TestImageBuildInfoList:
    def test_list_image_builds(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
        ))

        mock_item = MagicMock()
        mock_item.to_dict.return_value = {"metadata": {"name": "b1"}}
        mock_response = MagicMock()
        mock_response.items = [mock_item]
        mock_response.metadata.to_dict.return_value = {"continue": "abc"}

        with patch(f'{IB_CLASS}.list_image_builds', return_value=mock_response) as mock_list, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            mock_list.assert_called_once()
            result = mock_exit.call_args[1]['result']
            assert result['data'] == [{"metadata": {"name": "b1"}}]
            assert result['metadata'] == {"continue": "abc"}

    def test_list_with_filters(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            label_selector='env=prod',
            limit=5,
        ))

        mock_response = MagicMock()
        mock_response.items = []
        mock_response.metadata.to_dict.return_value = {}

        with patch(f'{IB_CLASS}.list_image_builds', return_value=mock_response) as mock_list, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            call_kwargs = mock_list.call_args[1]
            assert call_kwargs['label_selector'] == 'env=prod'
            assert call_kwargs['limit'] == 5


class TestImageBuildInfoGet:
    def test_get_by_name(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            name='my-build',
        ))

        mock_resource = MagicMock()
        mock_resource.to_dict.return_value = {"metadata": {"name": "my-build"}}

        with patch(f'{IB_CLASS}.get_image_build', return_value=mock_resource) as mock_get, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            mock_get.assert_called_once()
            result = mock_exit.call_args[1]['result']
            assert result['data'] == [{"metadata": {"name": "my-build"}}]

    def test_get_not_found_returns_empty(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            name='missing',
        ))

        with patch(f'{IB_CLASS}.get_image_build', return_value=None), \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            result = mock_exit.call_args[1]['result']
            assert result['data'] == []


class TestImageBuildInfoLog:
    def test_get_log(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            name='my-build',
            log=True,
        ))

        with patch(f'{IB_CLASS}.get_image_build_log', return_value='Step 1/3: FROM base') as mock_log, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            mock_log.assert_called_once_with('my-build')
            result = mock_exit.call_args[1]['result']
            assert result['log'] == 'Step 1/3: FROM base'

    def test_log_without_name_fails(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            log=True,
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            assert 'name is required' in mock_fail.call_args[1]['msg']


class TestImageBuildInfoValidation:
    def test_download_not_supported_for_image_build(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            name='my-build',
            download=True,
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            assert 'download is only supported for kind=ImageExport' in mock_fail.call_args[1]['msg']


class TestImageExportInfoList:
    def test_list_image_exports(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
        ))

        mock_item = MagicMock()
        mock_item.to_dict.return_value = {"metadata": {"name": "e1"}}
        mock_response = MagicMock()
        mock_response.items = [mock_item]
        mock_response.metadata.to_dict.return_value = {}

        with patch(f'{IB_CLASS}.list_image_exports', return_value=mock_response) as mock_list, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            mock_list.assert_called_once()
            result = mock_exit.call_args[1]['result']
            assert len(result['data']) == 1


class TestImageExportInfoGet:
    def test_get_by_name(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            name='my-export',
        ))

        mock_resource = MagicMock()
        mock_resource.to_dict.return_value = {"metadata": {"name": "my-export"}}

        with patch(f'{IB_CLASS}.get_image_export', return_value=mock_resource), \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            result = mock_exit.call_args[1]['result']
            assert result['data'] == [{"metadata": {"name": "my-export"}}]

    def test_get_not_found_returns_empty(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            name='missing',
        ))

        with patch(f'{IB_CLASS}.get_image_export', return_value=None), \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            result = mock_exit.call_args[1]['result']
            assert result['data'] == []


class TestImageExportInfoLog:
    def test_get_log(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            name='my-export',
            log=True,
        ))

        with patch(f'{IB_CLASS}.get_image_export_log', return_value='exporting...') as mock_log, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            mock_log.assert_called_once_with('my-export')
            result = mock_exit.call_args[1]['result']
            assert result['log'] == 'exporting...'

    def test_log_without_name_fails(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            log=True,
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            assert 'name is required' in mock_fail.call_args[1]['msg']


class TestImageExportInfoDownload:
    def test_download(self, tmp_path):
        dest = str(tmp_path / 'artifact.img')
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            name='my-export',
            download=True,
            dest=dest,
        ))

        artifact = bytearray(b'\x89PNG\r\n')

        with patch(f'{IB_CLASS}.download_image_export', return_value=artifact) as mock_dl, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            mock_dl.assert_called_once_with('my-export')
            result = mock_exit.call_args[1]['result']
            assert result['dest'] == dest
            with open(dest, 'rb') as f:
                assert f.read() == bytes(artifact)

    def test_download_without_name_fails(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            download=True,
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            assert 'name is required' in mock_fail.call_args[1]['msg']

    def test_log_and_download_mutually_exclusive(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            name='my-export',
            log=True,
            download=True,
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder_info import main
                main()

            assert 'mutually exclusive' in mock_fail.call_args[1]['msg']
