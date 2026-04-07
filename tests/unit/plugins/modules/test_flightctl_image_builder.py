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


def _run_module(exit_kwargs):
    """Run the module and capture the exit/fail JSON."""
    from plugins.modules.flightctl_image_builder import main
    with pytest.raises(SystemExit):
        main()
    return exit_kwargs


class TestImageBuilderCreate:
    def test_create_image_build(self):
        definition = {"apiVersion": "v1alpha1", "kind": "ImageBuild", "metadata": {"name": "b1"}, "spec": {}}
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            state='present',
            resource_definition=definition,
        ))

        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"metadata": {"name": "b1"}}

        with patch(f'{IB_CLASS}.create_image_build', return_value=mock_result) as mock_create, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_create.assert_called_once_with(definition)
            mock_exit.assert_called_once()
            call_kwargs = mock_exit.call_args[1]
            assert call_kwargs['changed'] is True
            assert call_kwargs['result'] == {"metadata": {"name": "b1"}}

    def test_create_image_export(self):
        definition = {"apiVersion": "v1alpha1", "kind": "ImageExport", "metadata": {"name": "e1"}, "spec": {}}
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            state='present',
            resource_definition=definition,
        ))

        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"metadata": {"name": "e1"}}

        with patch(f'{IB_CLASS}.create_image_export', return_value=mock_result) as mock_create, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_create.assert_called_once_with(definition)
            call_kwargs = mock_exit.call_args[1]
            assert call_kwargs['changed'] is True

    def test_create_missing_definition_fails(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            state='present',
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_fail.assert_called_once()
            assert 'resource_definition is required' in mock_fail.call_args[1]['msg']


class TestImageBuilderDelete:
    def test_delete_image_build_exists(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            name='b1',
            state='absent',
        ))

        mock_existing = MagicMock()
        with patch(f'{IB_CLASS}.get_image_build', return_value=mock_existing), \
             patch(f'{IB_CLASS}.delete_image_build') as mock_delete, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_delete.assert_called_once_with('b1')
            call_kwargs = mock_exit.call_args[1]
            assert call_kwargs['changed'] is True
            assert call_kwargs['result'] == {}

    def test_delete_image_build_not_found(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            name='b1',
            state='absent',
        ))

        with patch(f'{IB_CLASS}.get_image_build', return_value=None), \
             patch(f'{IB_CLASS}.delete_image_build') as mock_delete, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_delete.assert_not_called()
            call_kwargs = mock_exit.call_args[1]
            assert call_kwargs['changed'] is False

    def test_delete_image_export_exists(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            name='e1',
            state='absent',
        ))

        mock_existing = MagicMock()
        with patch(f'{IB_CLASS}.get_image_export', return_value=mock_existing), \
             patch(f'{IB_CLASS}.delete_image_export') as mock_delete, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_delete.assert_called_once_with('e1')

    def test_delete_missing_name_fails(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            state='absent',
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            assert 'name is required' in mock_fail.call_args[1]['msg']


class TestImageBuilderCancel:
    def test_cancel_image_build(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageBuild',
            name='b1',
            state='cancelled',
        ))

        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"metadata": {"name": "b1"}, "status": {"phase": "Cancelled"}}

        with patch(f'{IB_CLASS}.cancel_image_build', return_value=mock_result) as mock_cancel, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_cancel.assert_called_once_with('b1')
            call_kwargs = mock_exit.call_args[1]
            assert call_kwargs['changed'] is True

    def test_cancel_image_export(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            name='e1',
            state='cancelled',
        ))

        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"metadata": {"name": "e1"}}

        with patch(f'{IB_CLASS}.cancel_image_export', return_value=mock_result) as mock_cancel, \
             patch(f'{IB_CLASS}.exit_json') as mock_exit:
            mock_exit.side_effect = SystemExit(0)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            mock_cancel.assert_called_once_with('e1')

    def test_cancel_missing_name_fails(self):
        set_module_args(dict(
            flightctl_host='https://ib.example.com',
            flightctl_token='tok',
            kind='ImageExport',
            state='cancelled',
        ))

        with patch(f'{IB_CLASS}.fail_json') as mock_fail:
            mock_fail.side_effect = SystemExit(1)
            with pytest.raises(SystemExit):
                from plugins.modules.flightctl_image_builder import main
                main()

            assert 'name is required' in mock_fail.call_args[1]['msg']
