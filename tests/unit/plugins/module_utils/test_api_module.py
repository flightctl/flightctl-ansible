from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.utils import set_module_args

from plugins.module_utils.api_module import FlightctlAPIModule, ListResult
from plugins.module_utils.constants import API_MAPPING, ResourceType
from plugins.module_utils.exceptions import FlightctlException
from plugins.module_utils.options import ApprovalOptions, GetOptions
from plugins.module_utils.sdk_utils import is_pydantic_validation_error

from flightctl.api.enrollmenthookpolicy_api import EnrollmenthookpolicyApi
from flightctl.exceptions import ApiException, NotFoundException
from flightctl.models.auth_provider import AuthProvider
from flightctl.models.enrollment_request_approval import EnrollmentRequestApproval
from flightctl.models.certificate_signing_request import CertificateSigningRequest
from flightctl.models.enrollment_hook_policy import EnrollmentHookPolicy
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
    # username/password now triggers an OIDC password grant during construction
    # (EDM-5200); patch it so no network call is made in unit tests.
    with patch(
        'plugins.module_utils.api_module.oidc_password_grant',
        return_value='oidc-bearer-token',
    ):
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
def test_username_password_uses_oidc_bearer(mock_api, api_module_with_user_pass):
    # With username/password (no token), set_auth() performs an OIDC password
    # grant and sends a Bearer token — never HTTP Basic Auth (EDM-5200).
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


def test_set_auth_calls_oidc_grant_with_base_host():
    # The OIDC grant must receive the base host with any /api/v1 suffix stripped,
    # matching the inventory plugin (EDM-5200).
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/api/v1',
        flightctl_username='test-user',
        flightctl_password='test-pass',
        flightctl_validate_certs=False,
    ))
    with patch(
        'plugins.module_utils.api_module.oidc_password_grant',
        return_value='oidc-bearer-token',
    ) as mock_grant:
        module = FlightctlAPIModule(argument_spec={})

    mock_grant.assert_called_once_with(
        'https://test-flightctl-url.com', 'test-user', 'test-pass', False, None
    )
    assert module.headers == {'Authorization': 'Bearer oidc-bearer-token'}


def test_set_auth_never_sends_basic_auth():
    # Regression guard for EDM-5200: no code path may emit a Basic Auth header.
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_username='test-user',
        flightctl_password='test-pass',
    ))
    with patch(
        'plugins.module_utils.api_module.oidc_password_grant',
        return_value='oidc-bearer-token',
    ):
        module = FlightctlAPIModule(argument_spec={})

    assert module.headers is not None
    assert not module.headers['Authorization'].startswith('Basic ')


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


# --- EnrollmentHookPolicy tests ---

@pytest.fixture
def enrollment_hook_policy_definition():
    return {
        "apiVersion": "flightctl.io/v1beta1",
        "kind": "EnrollmentHookPolicy",
        "metadata": {"name": "test-enrollment-hook-policy"},
        "spec": {
            "afterEnrolling": {
                "failurePolicy": "Block",
                "controlPlaneActions": [
                    {
                        "url": "https://example.com/hooks/enrollment",
                        "timeout": "30s",
                        "retry": {
                            "maxAttempts": 3,
                            "backoffPolicy": "exponential",
                            "backoffDelay": "2s",
                            "maxBackoff": "2m",
                            "deadline": "10m",
                        },
                        "auth": {"bearerToken": "test-token"},
                    }
                ],
            }
        },
    }


def test_enrollment_hook_policy_mapping():
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    assert mapping.api is EnrollmenthookpolicyApi
    assert mapping.model is EnrollmentHookPolicy
    assert mapping.api_version == "v1beta1"
    assert mapping.get == "get_enrollment_hook_policy"
    assert mapping.list == "list_enrollment_hook_policies"
    assert mapping.create == "create_enrollment_hook_policy"
    assert mapping.patch == "patch_enrollment_hook_policy"
    assert mapping.replace == "replace_enrollment_hook_policy"
    assert mapping.delete == "delete_enrollment_hook_policy"


def test_get_enrollment_hook_policy(api_module):
    mock_api_instance = MagicMock()
    mock_policy = MagicMock(spec=EnrollmentHookPolicy)
    mock_api_instance.get_enrollment_hook_policy.return_value = mock_policy
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        result = api_module.get(GetOptions(
            resource=ResourceType.ENROLLMENT_HOOK_POLICY,
            name="test-enrollment-hook-policy",
        ))

    mock_api_instance.get_enrollment_hook_policy.assert_called_once_with(
        "test-enrollment-hook-policy", _headers=None, _request_timeout=10
    )
    assert result == mock_policy


def test_list_enrollment_hook_policies(api_module):
    mock_api_instance = MagicMock()
    mock_list_response = MagicMock()
    mock_api_instance.list_enrollment_hook_policies.return_value = mock_list_response
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        result = api_module.list(GetOptions(
            resource=ResourceType.ENROLLMENT_HOOK_POLICY,
            label_selector="environment=test",
            limit=10,
        ))

    mock_api_instance.list_enrollment_hook_policies.assert_called_once_with(
        label_selector="environment=test", limit=10,
        _headers=None, _request_timeout=10,
    )
    assert result == mock_list_response


def test_create_enrollment_hook_policy(api_module, enrollment_hook_policy_definition):
    mock_api_instance = MagicMock()
    mock_response = MagicMock(spec=EnrollmentHookPolicy)
    mock_api_instance.create_enrollment_hook_policy.return_value = mock_response
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        result = api_module.create(
            ResourceType.ENROLLMENT_HOOK_POLICY,
            enrollment_hook_policy_definition,
        )

    request = mock_api_instance.create_enrollment_hook_policy.call_args.args[0]
    action = request.spec.after_enrolling.control_plane_actions[0]
    assert isinstance(request, EnrollmentHookPolicy)
    assert request.spec.after_enrolling.failure_policy == "Block"
    assert action.url == "https://example.com/hooks/enrollment"
    assert action.timeout == "30s"
    assert action.retry.max_attempts == 3
    assert action.retry.backoff_policy == "exponential"
    assert action.retry.backoff_delay == "2s"
    assert action.retry.max_backoff == "2m"
    assert action.retry.deadline == "10m"
    assert action.auth.bearer_token.get_secret_value() == "test-token"
    mock_api_instance.create_enrollment_hook_policy.assert_called_once_with(
        request, _headers=None, _request_timeout=10
    )
    assert result == mock_response


def test_update_enrollment_hook_policy(api_module, enrollment_hook_policy_definition):
    existing = EnrollmentHookPolicy.from_dict(enrollment_hook_policy_definition)
    desired = dict(enrollment_hook_policy_definition)
    desired["spec"] = {
        "afterEnrolling": {
            "failurePolicy": "Continue",
            "controlPlaneActions": [
                {"url": "https://example.com/hooks/enrollment", "timeout": "45s"}
            ],
        }
    }
    mock_api_instance = MagicMock()
    mock_response = MagicMock(spec=EnrollmentHookPolicy)
    mock_api_instance.patch_enrollment_hook_policy.return_value = mock_response
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        changed, result = api_module.update(
            ResourceType.ENROLLMENT_HOOK_POLICY, existing, desired
        )

    call_args = mock_api_instance.patch_enrollment_hook_policy.call_args
    assert call_args.args[0] == "test-enrollment-hook-policy"
    patch_items = {
        patch_item.to_dict()["path"]: patch_item.to_dict()
        for patch_item in call_args.args[1]
    }
    assert patch_items == {
        "/spec/afterEnrolling/controlPlaneActions": {
            "op": "replace",
            "path": "/spec/afterEnrolling/controlPlaneActions",
            "value": [
                {"url": "https://example.com/hooks/enrollment", "timeout": "45s"}
            ],
        },
        "/spec/afterEnrolling/failurePolicy": {
            "op": "replace",
            "path": "/spec/afterEnrolling/failurePolicy",
            "value": "Continue",
        },
    }
    assert call_args.kwargs == {"_headers": None, "_request_timeout": 10}
    assert changed is True
    assert result == mock_response


def test_replace_enrollment_hook_policy(api_module, enrollment_hook_policy_definition):
    mock_api_instance = MagicMock()
    mock_response = MagicMock(spec=EnrollmentHookPolicy)
    mock_api_instance.replace_enrollment_hook_policy.return_value = mock_response
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        result = api_module.replace(
            ResourceType.ENROLLMENT_HOOK_POLICY,
            enrollment_hook_policy_definition,
        )

    call_args = mock_api_instance.replace_enrollment_hook_policy.call_args
    assert call_args.args[0] == "test-enrollment-hook-policy"
    assert isinstance(call_args.args[1], EnrollmentHookPolicy)
    assert call_args.kwargs == {"_headers": None, "_request_timeout": 10}
    assert result == mock_response


def test_delete_enrollment_hook_policy(api_module):
    mock_api_instance = MagicMock()
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        api_module.delete(
            ResourceType.ENROLLMENT_HOOK_POLICY,
            "test-enrollment-hook-policy",
        )

    mock_api_instance.delete_enrollment_hook_policy.assert_called_once_with(
        "test-enrollment-hook-policy", _headers=None, _request_timeout=10
    )


def test_enrollment_hook_policy_requires_after_enrolling(
        api_module, enrollment_hook_policy_definition):
    invalid_definition = dict(enrollment_hook_policy_definition)
    invalid_definition["spec"] = {}
    mock_api_instance = MagicMock()
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        with pytest.raises(ValueError, match="afterEnrolling"):
            api_module.create(
                ResourceType.ENROLLMENT_HOOK_POLICY,
                invalid_definition,
            )

    mock_api_instance.create_enrollment_hook_policy.assert_not_called()


def test_enrollment_hook_policy_status_conditions_serialize(
        enrollment_hook_policy_definition):
    response = dict(enrollment_hook_policy_definition)
    response["status"] = {
        "conditions": [
            {
                "status": "True",
                "observedGeneration": 2,
                "lastTransitionTime": "2026-01-01T00:00:00Z",
                "message": "Enrollment hooks are configured",
                "reason": "Configured",
                "type": "EnrollmentHooks",
            }
        ]
    }

    serialized = EnrollmentHookPolicy.from_dict(response).to_dict()
    condition = serialized["status"]["conditions"][0]

    assert condition["status"] == "True"
    assert condition["observedGeneration"] == 2
    assert condition["lastTransitionTime"].isoformat() == "2026-01-01T00:00:00+00:00"
    assert condition["message"] == "Enrollment hooks are configured"
    assert condition["reason"] == "Configured"
    assert condition["type"] == "EnrollmentHooks"


def test_enrollment_hook_policy_authentication_output_is_masked_and_serializable(
        enrollment_hook_policy_definition):
    policy = EnrollmentHookPolicy.from_dict(enrollment_hook_policy_definition)

    serialized = ListResult(data=[policy]).to_dict()
    bearer_token = serialized["data"][0]["spec"]["afterEnrolling"][
        "controlPlaneActions"
    ][0]["auth"]["bearerToken"]

    assert bearer_token == "*****"
    assert "test-token" not in json.dumps(serialized)


def test_enrollment_hook_policy_masked_output_can_be_reused_for_replace(
        api_module, enrollment_hook_policy_definition):
    policy = EnrollmentHookPolicy.from_dict(enrollment_hook_policy_definition)
    definition = ListResult(data=[policy]).to_dict()["data"][0]
    definition["spec"]["afterEnrolling"]["failurePolicy"] = "Continue"
    mock_api_instance = MagicMock()
    mock_api_instance.replace_enrollment_hook_policy.return_value = policy
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        api_module.replace(ResourceType.ENROLLMENT_HOOK_POLICY, definition)

    request = mock_api_instance.replace_enrollment_hook_policy.call_args.args[1]
    action = request.spec.after_enrolling.control_plane_actions[0]
    assert request.spec.after_enrolling.failure_policy == "Continue"
    assert action.auth.bearer_token.get_secret_value() == "*****"


@pytest.mark.parametrize(
    ("operation", "api_method", "error_match"),
    [
        ("get", "get_enrollment_hook_policy", "Unable to fetch EnrollmentHookPolicy"),
        ("list", "list_enrollment_hook_policies", "Unable to list EnrollmentHookPolicy"),
        ("create", "create_enrollment_hook_policy", "Unable to create EnrollmentHookPolicy"),
        ("update", "patch_enrollment_hook_policy", "Unable to update EnrollmentHookPolicy"),
        ("replace", "replace_enrollment_hook_policy", "Unable to replace EnrollmentHookPolicy"),
        ("delete", "delete_enrollment_hook_policy", "Unable to delete EnrollmentHookPolicy"),
    ],
)
def test_enrollment_hook_policy_api_errors(
        api_module, enrollment_hook_policy_definition,
        operation, api_method, error_match):
    mock_api_instance = MagicMock()
    getattr(mock_api_instance, api_method).side_effect = ApiException("server error")
    mapping = API_MAPPING[ResourceType.ENROLLMENT_HOOK_POLICY]
    existing = EnrollmentHookPolicy.from_dict(enrollment_hook_policy_definition)
    desired = dict(enrollment_hook_policy_definition)
    desired["metadata"] = {
        "name": "test-enrollment-hook-policy",
        "labels": {"updated": "true"},
    }

    with patch.object(mapping, 'api', return_value=mock_api_instance):
        with pytest.raises(FlightctlException, match=error_match):
            if operation == "get":
                api_module.get(GetOptions(
                    resource=ResourceType.ENROLLMENT_HOOK_POLICY,
                    name="test-enrollment-hook-policy",
                ))
            elif operation == "list":
                api_module.list(GetOptions(
                    resource=ResourceType.ENROLLMENT_HOOK_POLICY,
                ))
            elif operation == "create":
                api_module.create(
                    ResourceType.ENROLLMENT_HOOK_POLICY,
                    enrollment_hook_policy_definition,
                )
            elif operation == "update":
                api_module.update(
                    ResourceType.ENROLLMENT_HOOK_POLICY,
                    existing,
                    desired,
                )
            elif operation == "replace":
                api_module.replace(
                    ResourceType.ENROLLMENT_HOOK_POLICY,
                    enrollment_hook_policy_definition,
                )
            else:
                api_module.delete(
                    ResourceType.ENROLLMENT_HOOK_POLICY,
                    "test-enrollment-hook-policy",
                )


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
        mock_api_instance.get_catalog_item.assert_called_once_with(
            "my-catalog", "my-item", _headers=None, _request_timeout=10
        )
        mock_api_instance.get_catalog_item_deployments.assert_not_called()
        assert result == mock_item


def test_get_catalog_item_deployments(api_module):
    mock_api_instance = MagicMock()
    mock_deployment = MagicMock()
    mock_deployment.to_dict.return_value = {"catalog": "my-catalog", "catalogItem": "my-item"}
    mock_metadata = MagicMock()
    mock_metadata.to_dict.return_value = {"continue": None}
    mock_deployments = MagicMock()
    mock_deployments.items = [mock_deployment]
    mock_deployments.metadata = mock_metadata
    mock_api_instance.get_catalog_item_deployments.return_value = mock_deployments

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG_ITEM: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            get='get_catalog_item',
            deployments='get_catalog_item_deployments',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(
            resource=ResourceType.CATALOG_ITEM,
            name="my-item",
            catalog_name="my-catalog",
            deployments=True,
            limit=10,
            continue_token="next-page",
        )
        result = api_module.get_one_or_many(options)

        mock_api_instance.get_catalog_item_deployments.assert_called_once_with(
            "my-catalog", "my-item", limit=10, var_continue="next-page", _headers=None, _request_timeout=10
        )
        mock_api_instance.get_catalog_item.assert_not_called()
        assert result.to_dict() == {
            "data": [{"catalog": "my-catalog", "catalogItem": "my-item"}],
            "metadata": {"continue": None},
        }


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
        mock_api_instance.list_catalog_items.assert_called_once_with(
            "my-catalog", _headers=None, _request_timeout=10
        )
        mock_api_instance.get_catalog_item_deployments.assert_not_called()
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


def test_get_catalog_item_deployments_pydantic_fallback(api_module):
    deployments_json = {
        "items": [{"catalog": "my-catalog", "catalogItem": "my-item"}],
        "metadata": {"continue": None},
    }
    mock_api_instance = MagicMock()
    mock_api_instance.get_catalog_item_deployments.side_effect = _make_pydantic_error()
    mock_api_instance.get_catalog_item_deployments_without_preload_content.return_value = _raw_response(
        deployments_json
    )

    with patch.dict('plugins.module_utils.constants.API_MAPPING', {
        ResourceType.CATALOG_ITEM: MagicMock(
            api=MagicMock(return_value=mock_api_instance),
            api_version='v1alpha1',
            get='get_catalog_item',
            deployments='get_catalog_item_deployments',
        ),
    }):
        from plugins.module_utils.options import GetOptions
        options = GetOptions(
            resource=ResourceType.CATALOG_ITEM,
            name="my-item",
            catalog_name="my-catalog",
            deployments=True,
            limit=10,
            continue_token="next-page",
        )
        result = api_module.get_one_or_many(options)

        mock_api_instance.get_catalog_item_deployments_without_preload_content.assert_called_once_with(
            "my-catalog", "my-item", limit=10, var_continue="next-page", _headers=None, _request_timeout=10
        )
        assert result.to_dict() == {
            "data": [{"catalog": "my-catalog", "catalogItem": "my-item"}],
            "metadata": {"continue": None},
        }


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
