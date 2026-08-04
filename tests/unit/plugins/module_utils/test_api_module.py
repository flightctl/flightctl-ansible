from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.utils import set_module_args

from plugins.module_utils.api_module import FlightctlAPIModule
from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import FlightctlException
from plugins.module_utils.options import ApprovalOptions

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
    with patch('plugins.module_utils.api_module.oidc_password_grant', return_value=('oidc-bearer-token', None)):
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
def test_username_password_uses_oidc_bearer_token(mock_api, api_module_with_user_pass):
    """username/password must be exchanged for a Bearer token via OIDC, never sent as Basic auth."""
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
        _headers={'Authorization': 'Bearer oidc-bearer-token'},
        _request_timeout=10
    )


def test_username_password_performs_oidc_grant_with_module_connection_params():
    """set_auth() should forward the module's host/verify_ssl/ca_path/timeout to the OIDC helper."""
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_username='test-user',
        flightctl_password='test-pass',
        flightctl_validate_certs=False,
    ))
    with patch(
        'plugins.module_utils.api_module.oidc_password_grant',
        return_value=('oidc-bearer-token', None),
    ) as mock_grant:
        module = FlightctlAPIModule(argument_spec={})

    mock_grant.assert_called_once_with(
        host=module.host,
        username='test-user',
        password='test-pass',
        verify_ssl=False,
        ca_path=None,
        request_timeout=10,
    )
    assert module.headers == {'Authorization': 'Bearer oidc-bearer-token'}
    # Credentials are no longer needed once a bearer token has been obtained.
    assert module.username is None
    assert module.password is None


def test_username_password_oidc_failure_fails_module():
    """A failed OIDC grant should fail the module with the upstream error detail, not silently fall back."""
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_username='test-user',
        flightctl_password='test-pass',
    ))
    with patch(
        'plugins.module_utils.api_module.oidc_password_grant',
        return_value=(None, 'the server has no OIDC-based authentication provider configured'),
    ), patch.object(FlightctlAPIModule, 'fail_json', side_effect=SystemExit(1)) as mock_fail:
        with pytest.raises(SystemExit):
            FlightctlAPIModule(argument_spec={})

    assert 'no OIDC-based authentication provider configured' in mock_fail.call_args.kwargs['msg']


def test_username_password_oidc_failure_with_non_raising_error_callback_still_raises():
    """
    fail_json() only raises/exits when no error_callback is set. If a caller supplies a
    non-raising error_callback, set_auth() must still stop instead of falling through to
    sending "Authorization: Bearer None".
    """
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_username='test-user',
        flightctl_password='test-pass',
    ))
    with patch(
        'plugins.module_utils.api_module.oidc_password_grant',
        return_value=(None, 'the server has no OIDC-based authentication provider configured'),
    ):
        with pytest.raises(FlightctlException):
            FlightctlAPIModule(argument_spec={}, error_callback=MagicMock())


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
