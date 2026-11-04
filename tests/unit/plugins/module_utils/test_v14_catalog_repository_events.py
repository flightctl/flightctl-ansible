from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest
from flightctl.models.auth_provider import AuthProvider
from flightctl.models.event import Event
from flightctl.models.repository import Repository
from flightctl.v1alpha1.models.catalog_item import CatalogItem
from flightctl.v1alpha1.models.vulnerability import Vulnerability
from flightctl.v1alpha1.models.vulnerability_group_item import VulnerabilityGroupItem

from plugins.module_utils.api_module import FlightctlAPIModule, ListResult
from plugins.module_utils.constants import API_MAPPING, ResourceType
from tests.unit.utils import set_module_args


@pytest.fixture
def api_module():
    set_module_args(
        {
            "flightctl_host": "https://test-flightctl-url.com/",
            "flightctl_token": "test-token",
        }
    )
    return FlightctlAPIModule(argument_spec={})


def _repository_definition(**spec):
    return {
        "apiVersion": "flightctl.io/v1beta1",
        "kind": "Repository",
        "metadata": {"name": "delta-repository"},
        "spec": {
            "registry": "quay.io",
            "type": "oci",
            **spec,
        },
    }


def test_repository_oci_delta_fields_use_generic_create(api_module):
    definition = _repository_definition(
        repository="flightctl/deltas",
        deltaStorageTarget=True,
    )
    mock_api = MagicMock()
    mapping = API_MAPPING[ResourceType.REPOSITORY]

    with patch.object(mapping, "api", return_value=mock_api):
        api_module.create(ResourceType.REPOSITORY, definition)

    request = mock_api.create_repository.call_args.args[0]
    assert isinstance(request, Repository)
    assert request.spec.actual_instance.repository == "flightctl/deltas"
    assert request.spec.actual_instance.delta_storage_target is True


def test_repository_oci_namespace_and_delta_target_are_serialized(api_module):
    definition = _repository_definition(
        namespace="flightctl",
        deltaStorageTarget=True,
    )
    repository = Repository.from_dict(definition)
    serialized = ListResult(data=[repository]).to_dict()["data"][0]

    assert serialized["spec"]["namespace"] == "flightctl"
    assert serialized["spec"]["deltaStorageTarget"] is True


@pytest.mark.parametrize("operation", ["create", "replace", "update"])
def test_repository_rejects_mutually_exclusive_placement_fields(api_module, operation):
    definition = _repository_definition(
        repository="flightctl/deltas",
        namespace="flightctl",
    )

    with pytest.raises(ValueError, match="repository.*namespace.*mutually exclusive"):
        if operation == "create":
            api_module.create(ResourceType.REPOSITORY, definition)
        elif operation == "replace":
            api_module.replace(ResourceType.REPOSITORY, definition)
        else:
            existing = Repository.from_dict(
                _repository_definition(namespace="flightctl")
            )
            api_module.update(ResourceType.REPOSITORY, existing, definition)


def _auth_provider_definition(prompt):
    return {
        "apiVersion": "flightctl.io/v1beta1",
        "kind": "AuthProvider",
        "metadata": {"name": "oauth-provider"},
        "spec": {
            "providerType": "oauth2",
            "authorizationUrl": "https://issuer.example/authorize",
            "tokenUrl": "https://issuer.example/token",
            "userinfoUrl": "https://issuer.example/userinfo",
            "clientId": "flightctl",
            "clientSecret": "secret",
            "prompt": prompt,
            "organizationAssignment": {
                "type": "static",
                "organizationName": "edge-org",
            },
            "roleAssignment": {"type": "static", "roles": ["viewer"]},
        },
    }


def test_auth_provider_prompt_round_trips_through_generic_create(api_module):
    definition = _auth_provider_definition("login consent")
    mock_api = MagicMock()
    mapping = API_MAPPING[ResourceType.AUTH_PROVIDER]

    with patch.object(mapping, "api", return_value=mock_api):
        api_module.create(ResourceType.AUTH_PROVIDER, definition)

    request = mock_api.create_auth_provider.call_args.args[0]
    assert isinstance(request, AuthProvider)
    assert request.spec.actual_instance.prompt == "login consent"
    assert request.to_dict()["spec"]["prompt"] == "login consent"


def test_auth_provider_rejects_non_printable_prompt():
    with pytest.raises(ValueError, match="regular expression"):
        AuthProvider.from_dict(_auth_provider_definition("login\nconsent"))


def _catalog_item_definition():
    return {
        "apiVersion": "flightctl.io/v1alpha1",
        "kind": "CatalogItem",
        "metadata": {"name": "edge-agent", "catalog": "edge-catalog"},
        "spec": {
            "type": "container",
            "artifacts": [{"type": "container", "uri": "quay.io/example/edge-agent"}],
            "versions": [
                {
                    "version": "1.2.3",
                    "references": {"container": "1.2.3"},
                    "channels": ["stable"],
                    "skipRange": ">=1.0.0 <2.0.0 || >=3.0.0",
                    "deviceFeatures": {
                        "gpu.present": "true",
                        "kvm.enabled": "false",
                        "os.mode": "image",
                    },
                }
            ],
        },
    }


def test_catalog_item_device_features_and_semver_alternatives_use_generic_create(
    api_module,
):
    definition = _catalog_item_definition()
    mock_api = MagicMock()
    mapping = API_MAPPING[ResourceType.CATALOG_ITEM]

    with patch.object(mapping, "api", return_value=mock_api):
        api_module.create(ResourceType.CATALOG_ITEM, definition, "edge-catalog")

    request = mock_api.create_catalog_item.call_args.args[1]
    assert isinstance(request, CatalogItem)
    version = request.spec.versions[0]
    assert version.skip_range == ">=1.0.0 <2.0.0 || >=3.0.0"
    assert version.device_features.gpu_present.value == "true"
    assert version.device_features.os_mode.value == "image"


def test_catalog_item_info_preserves_device_features_and_semver_alternatives():
    item = CatalogItem.from_dict(_catalog_item_definition())
    serialized = ListResult(data=[item]).to_dict()["data"][0]
    version = serialized["spec"]["versions"][0]

    assert version["skipRange"] == ">=1.0.0 <2.0.0 || >=3.0.0"
    assert version["deviceFeatures"] == {
        "gpu.present": "true",
        "kvm.enabled": "false",
        "os.mode": "image",
    }


def _event_definition(reason, details=None):
    return {
        "apiVersion": "flightctl.io/v1beta1",
        "kind": "Event",
        "metadata": {"name": "delta-event"},
        "involvedObject": {"kind": "Fleet", "name": "edge-fleet"},
        "reason": reason,
        "message": "delta event",
        "details": details,
        "type": "Normal",
        "source": {"component": "controller"},
        "actor": "service:controller",
    }


@pytest.mark.parametrize(
    "reason",
    [
        "PrepareDeltas",
        "DeltaGenerationProgress",
        "DeltaGenerationCompleted",
        "EnrollmentHookSucceeded",
        "EnrollmentHookFailed",
        "EnrollmentHookNotifyFailed",
        "EnrollmentHookManualOverride",
    ],
)
def test_event_v14_reasons_are_accepted_by_info_output(reason):
    event = Event.from_dict(_event_definition(reason))
    serialized = ListResult(data=[event]).to_dict()["data"][0]
    assert serialized["reason"] == reason


def test_event_delta_detail_variant_is_preserved_by_info_output():
    event = Event.from_dict(
        _event_definition(
            "DeltaGenerationProgress",
            {
                "detailType": "DeltaGenerationProgress",
                "imageRepository": "quay.io/example/deltas",
                "sourceDigest": "sha256:source",
                "targetDigest": "sha256:target",
                "generationStatus": "succeeded",
                "phase": "push",
                "templateVersion": "2",
                "generation": 3,
            },
        )
    )
    serialized = ListResult(data=[event]).to_dict()["data"][0]

    assert serialized["details"]["detailType"] == "DeltaGenerationProgress"
    assert serialized["details"]["generation"] == 3
    assert serialized["details"]["phase"] == "push"


def test_vulnerability_sources_are_preserved_in_info_output():
    vulnerability = Vulnerability.from_dict(
        {
            "apiVersion": "flightctl.io/v1alpha1",
            "kind": "Vulnerability",
            "cveId": "CVE-2026-0001",
            "severity": "High",
            "source": "trustify",
        }
    )
    grouped = VulnerabilityGroupItem.from_dict(
        {
            "imageDigest": "sha256:image",
            "imageRefs": ["quay.io/example/app:1"],
            "severity": "Medium",
            "source": "quay",
        }
    )
    serialized = ListResult(data=[vulnerability, grouped]).to_dict()["data"]

    assert serialized[0]["source"] == "trustify"
    assert serialized[1]["source"] == "quay"
