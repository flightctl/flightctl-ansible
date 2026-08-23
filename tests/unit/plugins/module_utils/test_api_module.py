from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.utils import set_module_args

from plugins.module_utils.api_module import FlightctlAPIModule
from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import FlightctlException
from plugins.module_utils.options import ApprovalOptions
from plugins.module_utils.sdk_utils import is_pydantic_validation_error

from flightctl.exceptions import ApiException, NotFoundException
from flightctl.models.auth_provider import AuthProvider
from flightctl.models.enrollment_request_approval import EnrollmentRequestApproval
from flightctl.models.certificate_signing_request import CertificateSigningRequest
from flightctl.v1alpha1.exceptions import (
    NotFoundException as V1Alpha1NotFoundException,
)
from flightctl.v1alpha1.models.catalog import Catalog
from flightctl.v1alpha1.models.catalog_item import CatalogItem


@pytest.fixture
def api_module():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_config_file='tests/unit/plugins/module_utils/fixtures/client.yaml'
    ))
    return FlightctlAPIModule(argument_spec={})


@pytest.fixture
def api_module_with_token():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_token='test-token'
    ))
    return FlightctlAPIModule(argument_spec={})


@pytest.fixture
def api_module_with_user_pass():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_username='test-user',
        flightctl_password='test-pass'
    ))
    return FlightctlAPIModule(argument_spec={})


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_approve_enrollment_success(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", True)
    body = EnrollmentRequestApproval.from_dict(input.to_request_params())
    api_module.approve(input)
    mock_api_instance.approve_enrollment_request.assert_called_with(input.name, body, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_deny_enrollment_success(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", False)
    body = EnrollmentRequestApproval.from_dict(input.to_request_params())
    api_module.approve(input)
    mock_api_instance.approve_enrollment_request.assert_called_with(input.name, body, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_approve_404(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_api_instance.approve_enrollment_request.side_effect = NotFoundException()

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", True)
    with pytest.raises(FlightctlException, match="Unable to approve EnrollmentRequest - test-enrollment: *"):
        api_module.approve(input)


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_approve_csr(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.get_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", True)
    api_module.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(input.name, mock_csr, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_deny_csr(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.get_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", False)
    api_module.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(input.name, mock_csr, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_token_auth(mock_api, api_module_with_token):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.get_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", True)
    api_module_with_token.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(
        input.name,
        mock_csr,
        _headers={'Authorization': 'Bearer test-token'},
        _request_timeout=10
    )


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_basic_auth(mock_api, api_module_with_user_pass):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.get_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", True)
    api_module_with_user_pass.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(
        input.name,
        mock_csr,
        _headers={'Authorization': 'Basic dGVzdC11c2VyOnRlc3QtcGFzcw=='},
        _request_timeout=10
    )


# --- AuthProvider tests ---

def test_get_auth_provider(api_module):
    mock_api_instance = MagicMock()
    mock_provider = MagicMock(spec=AuthProvider)
    mock_api_instance.get_auth_provider.return_value = mock_provider

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.AUTH_PROVIDER: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            get='get_auth_provider',
            list='list_auth_providers',
            create='create_auth_provider',
            patch='patch_auth_provider',
            replace='replace_auth_provider',
            delete='delete_auth_provider',
            rendered=None,
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.AUTH_PROVIDER, name="test-provider")
        result = api_module.get(options)
        mock_api_instance.get_auth_provider.assert_called_once()
        assert result == mock_provider


def test_get_auth_provider_not_found(api_module):
    mock_api_instance = MagicMock()
    mock_api_instance.get_auth_provider.side_effect = NotFoundException()

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.AUTH_PROVIDER: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            get='get_auth_provider',
            rendered=None,
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.AUTH_PROVIDER, name="missing-provider")
        result = api_module.get(options)
        assert result is None


def test_list_auth_providers(api_module):
    mock_api_instance = MagicMock()
    mock_list_response = MagicMock()
    mock_api_instance.list_auth_providers.return_value = mock_list_response

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.AUTH_PROVIDER: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_auth_providers',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.AUTH_PROVIDER)
        result = api_module.list(options)
        mock_api_instance.list_auth_providers.assert_called_once()
        assert result == mock_list_response


def test_delete_auth_provider(api_module):
    mock_api_instance = MagicMock()
    mock_api_instance.delete_auth_provider.return_value = None

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.AUTH_PROVIDER: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            delete='delete_auth_provider',
        ),
    }):
        api_module.delete(ResourceType.AUTH_PROVIDER, "test-provider", None)
        mock_api_instance.delete_auth_provider.assert_called_once()


# --- Event tests (list-only) ---

def test_list_events(api_module):
    mock_api_instance = MagicMock()
    mock_list_response = MagicMock()
    mock_api_instance.list_events.return_value = mock_list_response

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.EVENT: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_events',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.EVENT)
        result = api_module.list(options)
        mock_api_instance.list_events.assert_called_once()
        assert result == mock_list_response


def test_list_events_api_error(api_module):
    mock_api_instance = MagicMock()
    mock_api_instance.list_events.side_effect = ApiException("server error")

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.EVENT: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_events',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.EVENT)
        with pytest.raises(FlightctlException, match="Unable to list Event"):
            api_module.list(options)


# --- Organization tests (list-only) ---

def test_list_organizations(api_module):
    mock_api_instance = MagicMock()
    mock_list_response = MagicMock()
    mock_api_instance.list_organizations.return_value = mock_list_response

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.ORGANIZATION: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_organizations',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.ORGANIZATION)
        result = api_module.list(options)
        mock_api_instance.list_organizations.assert_called_once()
        assert result == mock_list_response


def test_list_organizations_api_error(api_module):
    mock_api_instance = MagicMock()
    mock_api_instance.list_organizations.side_effect = ApiException("server error")

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.ORGANIZATION: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_organizations',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.ORGANIZATION)
        with pytest.raises(FlightctlException, match="Unable to list Organization"):
            api_module.list(options)


# --- Catalog tests (v1alpha1) ---

def test_get_catalog(api_module):
    mock_api_instance = MagicMock()
    mock_catalog = MagicMock(spec=Catalog)
    mock_api_instance.get_catalog.return_value = mock_catalog

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            get='get_catalog',
            rendered=None,
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.CATALOG, name="test-catalog")
        result = api_module.get(options)
        mock_api_instance.get_catalog.assert_called_once()
        assert result == mock_catalog


def test_get_catalog_not_found(api_module):
    mock_api_instance = MagicMock()
    mock_api_instance.get_catalog.side_effect = V1Alpha1NotFoundException()

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            get='get_catalog',
            rendered=None,
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.CATALOG, name="missing")
        result = api_module.get(options)
        assert result is None


def test_list_catalogs(api_module):
    mock_api_instance = MagicMock()
    mock_list_response = MagicMock()
    mock_api_instance.list_catalogs.return_value = mock_list_response

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            list='list_catalogs',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.CATALOG)
        result = api_module.list(options)
        mock_api_instance.list_catalogs.assert_called_once()
        assert result == mock_list_response


def test_delete_catalog(api_module):
    mock_api_instance = MagicMock()
    mock_api_instance.delete_catalog.return_value = None

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            delete='delete_catalog',
        ),
    }):
        api_module.delete(ResourceType.CATALOG, "test-catalog")
        mock_api_instance.delete_catalog.assert_called_once()


# --- CatalogItem tests (v1alpha1 nested) ---

def test_get_catalog_item(api_module):
    mock_api_instance = MagicMock()
    mock_item = MagicMock(spec=CatalogItem)
    mock_api_instance.get_catalog_item.return_value = mock_item

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG_ITEM: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            get='get_catalog_item',
            rendered=None,
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.CATALOG_ITEM, name="my-item", catalog_name="my-catalog")
        result = api_module.get(options)
        mock_api_instance.get_catalog_item.assert_called_once()
        assert result == mock_item


def test_list_catalog_items(api_module):
    mock_api_instance = MagicMock()
    mock_list_response = MagicMock()
    mock_api_instance.list_catalog_items.return_value = mock_list_response

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG_ITEM: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            list='list_catalog_items',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.CATALOG_ITEM, catalog_name="my-catalog")
        result = api_module.list(options)
        mock_api_instance.list_catalog_items.assert_called_once()
        assert result == mock_list_response


def test_delete_catalog_item(api_module):
    mock_api_instance = MagicMock()
    mock_api_instance.delete_catalog_item.return_value = None

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG_ITEM: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            delete='delete_catalog_item',
        ),
    }):
        api_module.delete(ResourceType.CATALOG_ITEM, "my-item", "my-catalog")
        mock_api_instance.delete_catalog_item.assert_called_once()


# --- pydantic ValidationError raw-JSON fallback (EDM-5201) ---

def _make_pydantic_error(msg="ApplicationVolume requires image"):
    """Build an exception matching the pydantic ValidationError heuristic.

    Detection is by type name + module, so pydantic need not be installed.
    """
    class ValidationError(Exception):
        __module__ = "pydantic_core._pydantic_core"

    return ValidationError(msg)


def _raw_response(payload):
    resp = MagicMock()
    resp.data = json.dumps(payload).encode()
    return resp


def _real_sdk_pydantic_error():
    """Produce a *genuine* SDK pydantic ValidationError for the EDM-5201 scenario.

    Builds a device whose compose application has a mount-only ``ApplicationVolume``
    (no required ``image`` field) and lets the real SDK model raise. Returns the
    exception, or ``None`` if the SDK model shape changed so the caller can skip
    rather than fail spuriously.
    """
    try:
        from flightctl.models.device import Device

        Device.from_dict({
            "apiVersion": "v1beta1",
            "kind": "Device",
            "metadata": {"name": "edge-1"},
            "spec": {
                "applications": [
                    {
                        "name": "myapp",
                        "appType": "compose",
                        "image": "quay.io/app:latest",
                        "volumes": [
                            {"name": "data", "mount": {"type": "filesystem", "path": "/data"}}
                        ],
                    }
                ]
            },
        })
    except Exception as e:  # noqa: BLE001 - we want whatever the SDK raises
        return e
    return None


def test_get_device_real_sdk_pydantic_error_fallback(api_module):
    """End-to-end with a *genuine* SDK pydantic ValidationError (mount-only volume).

    Proves the ticket premise against the real SDK: the mount-only volume makes
    the SDK raise a real pydantic ValidationError, which get() must detect and
    recover from via the raw-JSON fallback.
    """
    real_err = _real_sdk_pydantic_error()
    if real_err is None or not is_pydantic_validation_error(real_err):
        pytest.skip("SDK did not raise a detectable pydantic ValidationError for this payload")

    device_json = {
        "metadata": {"name": "edge-1"},
        "spec": {
            "applications": [
                {"name": "myapp", "volumes": [{"name": "data", "mountPath": "/data"}]}
            ]
        },
    }
    mock_api_instance = MagicMock()
    mock_api_instance.get_device.side_effect = real_err
    mock_api_instance.get_device_without_preload_content.return_value = _raw_response(device_json)

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            get='get_device',
            rendered='get_rendered_device',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE, name="edge-1")
        result = api_module.get(options)

        mock_api_instance.get_device_without_preload_content.assert_called_once()
        assert result.to_dict() == device_json


def test_get_device_pydantic_fallback(api_module):
    """A device with a mount-only application volume (no image) must not crash get()."""
    device_json = {
        "metadata": {"name": "edge-1"},
        "spec": {
            "applications": [
                {"name": "app", "volumes": [{"name": "data", "mountPath": "/data"}]}
            ]
        },
    }
    mock_api_instance = MagicMock()
    mock_api_instance.get_device.side_effect = _make_pydantic_error()
    mock_api_instance.get_device_without_preload_content.return_value = _raw_response(device_json)

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            get='get_device',
            rendered='get_rendered_device',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE, name="edge-1")
        result = api_module.get(options)

        mock_api_instance.get_device_without_preload_content.assert_called_once()
        assert result.to_dict() == device_json


def test_get_rendered_device_pydantic_fallback(api_module):
    """The rendered device path must use the rendered raw endpoint for fallback."""
    device_json = {"metadata": {"name": "edge-1"}}
    mock_api_instance = MagicMock()
    mock_api_instance.get_rendered_device.side_effect = _make_pydantic_error()
    mock_api_instance.get_rendered_device_without_preload_content.return_value = _raw_response(device_json)

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            get='get_device',
            rendered='get_rendered_device',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE, name="edge-1", rendered=True)
        result = api_module.get(options)

        mock_api_instance.get_rendered_device_without_preload_content.assert_called_once()
        mock_api_instance.get_device_without_preload_content.assert_not_called()
        assert result.to_dict() == device_json


def test_get_non_pydantic_error_reraises(api_module):
    """Unexpected non-pydantic, non-API errors must propagate unchanged."""
    mock_api_instance = MagicMock()
    mock_api_instance.get_device.side_effect = RuntimeError("unexpected")

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            get='get_device',
            rendered='get_rendered_device',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE, name="edge-1")
        with pytest.raises(RuntimeError, match="unexpected"):
            api_module.get(options)
        mock_api_instance.get_device_without_preload_content.assert_not_called()


def test_get_raw_fallback_failure_raises_flightctl_exception(api_module):
    """If the raw fallback request itself fails, raise a clean FlightctlApiException."""
    mock_api_instance = MagicMock()
    mock_api_instance.get_device.side_effect = _make_pydantic_error()
    mock_api_instance.get_device_without_preload_content.side_effect = ConnectionError("timeout")

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            get='get_device',
            rendered='get_rendered_device',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE, name="edge-1")
        with pytest.raises(FlightctlException, match="Unable to fetch Device - edge-1"):
            api_module.get(options)


def test_list_devices_pydantic_fallback(api_module):
    """list() must fall back to raw JSON and preserve items/metadata/summary."""
    list_json = {
        "items": [
            {"metadata": {"name": "edge-1"}},
            {"metadata": {"name": "edge-2"}},
        ],
        "metadata": {"continue": "next-token"},
        "summary": {"total": 2},
    }
    mock_api_instance = MagicMock()
    mock_api_instance.list_devices.side_effect = _make_pydantic_error()
    mock_api_instance.list_devices_without_preload_content.return_value = _raw_response(list_json)

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_devices',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE)
        result = api_module.list(options)

        mock_api_instance.list_devices_without_preload_content.assert_called_once()
        assert [item.to_dict() for item in result.items] == list_json["items"]
        assert result.metadata.to_dict() == {"continue": "next-token"}
        assert result.summary.to_dict() == {"total": 2}


def test_get_one_or_many_list_fallback_serializes(api_module):
    """End-to-end: get_one_or_many + ListResult.to_dict() must work over the raw fallback."""
    list_json = {
        "items": [{"metadata": {"name": "edge-1"}}],
        "metadata": {"continue": None},
    }
    mock_api_instance = MagicMock()
    mock_api_instance.list_devices.side_effect = _make_pydantic_error()
    mock_api_instance.list_devices_without_preload_content.return_value = _raw_response(list_json)

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_devices',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE)
        result = api_module.get_one_or_many(options)

        serialized = result.to_dict()
        assert serialized["data"] == [{"metadata": {"name": "edge-1"}}]
        assert serialized["metadata"] == {"continue": None}


def test_list_raw_fallback_failure_raises_flightctl_exception(api_module):
    """If the raw list fallback request fails, raise a clean FlightctlApiException."""
    mock_api_instance = MagicMock()
    mock_api_instance.list_devices.side_effect = _make_pydantic_error()
    mock_api_instance.list_devices_without_preload_content.side_effect = ConnectionError("timeout")

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.DEVICE: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1beta1',
            list='list_devices',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(resource=ResourceType.DEVICE)
        with pytest.raises(FlightctlException, match="Unable to list Device"):
            api_module.list(options)
