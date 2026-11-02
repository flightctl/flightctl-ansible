from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest
from flightctl.models.application_image_digest import ApplicationImageDigest
from flightctl.models.device import Device
from flightctl.models.device_capabilities import DeviceCapabilities
from flightctl.models.device_os_spec import DeviceOsSpec
from flightctl.models.enrollment_request import EnrollmentRequest
from flightctl.models.fleet import Fleet
from flightctl.models.fleet_status import FleetStatus
from flightctl.models.image_spec import ImageSpec

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


def _device_status_definition():
    return {
        "conditions": [],
        "systemInfo": {
            "architecture": "x86_64",
            "bootID": "boot-1",
            "operatingSystem": "Fedora Linux",
            "agentVersion": "1.4.0",
            "bootcVersion": "1.7.2",
            "ociDeltaVersion": "0.6.0",
            "deltaEligible": True,
            "gpus": [{"index": 0, "vendor": "nvidia", "model": "A10"}],
            "kvm": {"enabled": True},
            "osMode": "image",
        },
        "applications": [
            {
                "name": "web",
                "ready": "1/1",
                "restarts": 0,
                "status": "Running",
                "embedded": False,
                "appType": "container",
                "lastDelta": {"outcome": "Applied"},
                "imageDigests": [
                    {"image": "quay.io/example/web:1", "digest": "sha256:abc"}
                ],
                "deltaSize": "245.3 MiB",
            }
        ],
        "applicationsSummary": {"status": "Healthy"},
        "resources": {"cpu": "Healthy", "memory": "Healthy", "disk": "Healthy"},
        "integrity": {"status": "Unknown"},
        "config": {"renderedVersion": "1"},
        "os": {
            "image": "quay.io/example/os:1",
            "imageDigest": "sha256:os",
            "deltaSize": "1 GiB",
            "lastDelta": {"outcome": "Applied"},
        },
        "updated": {"status": "UpToDate"},
        "summary": {"status": "Online"},
        "lifecycle": {"status": "Enrolled"},
        "deltaGeneration": {"completed": 1, "total": 2},
        "enrollmentHooks": {"snapshot": {"failurePolicy": "Continue"}},
        "systemInfoStatus": {
            "summary": {"status": "Healthy"},
            "statuses": {"systemInfo": {}, "customInfo": {}},
        },
    }


def test_device_v14_status_fields_round_trip_through_info_model():
    device = Device.from_dict(
        {
            "apiVersion": "flightctl.io/v1beta1",
            "kind": "Device",
            "metadata": {"name": "device-1"},
            "status": _device_status_definition(),
        }
    )
    serialized = ListResult(data=[device]).to_dict()["data"][0]["status"]

    assert serialized["deltaGeneration"] == {"completed": 1, "total": 2}
    assert serialized["enrollmentHooks"]["snapshot"]["failurePolicy"] == "Continue"
    assert serialized["systemInfoStatus"]["summary"]["status"] == "Healthy"
    assert serialized["systemInfo"]["bootcVersion"] == "1.7.2"
    assert serialized["systemInfo"]["ociDeltaVersion"] == "0.6.0"
    assert serialized["systemInfo"]["deltaEligible"] is True
    assert serialized["systemInfo"]["gpus"][0]["model"] == "A10"
    assert serialized["systemInfo"]["kvm"]["enabled"] is True
    assert serialized["systemInfo"]["osMode"] == "image"
    assert serialized["applications"][0]["imageDigests"][0]["digest"] == "sha256:abc"
    assert serialized["applications"][0]["lastDelta"]["outcome"] == "Applied"
    assert serialized["applications"][0]["deltaSize"] == "245.3 MiB"
    assert serialized["os"]["lastDelta"]["outcome"] == "Applied"
    assert serialized["os"]["deltaSize"] == "1 GiB"


def test_deprecated_capabilities_os_mode_is_preserved_with_system_info_mode():
    capabilities = DeviceCapabilities.from_dict({"osMode": "image"})
    system_info = Device.from_dict(
        {
            "apiVersion": "flightctl.io/v1beta1",
            "kind": "Device",
            "metadata": {"name": "device-1"},
            "status": _device_status_definition(),
        }
    ).status.system_info

    assert capabilities.to_dict() == {"osMode": "image"}
    assert system_info.to_dict()["osMode"] == "image"


def test_v14_read_only_image_fields_are_returned_through_info_serialization():
    image = ImageSpec.from_dict(
        {
            "image": "quay.io/example/web:1",
            "deltaImage": "quay.io/example/web:delta",
            "deltaImages": [
                {
                    "targetImage": "quay.io/example/sidecar:1",
                    "targetDigest": "sha256:sidecar",
                    "deltaImage": "quay.io/example/sidecar:delta",
                }
            ],
        }
    )
    device_os = DeviceOsSpec.from_dict(
        {"image": "quay.io/example/os:1", "deltaImage": "quay.io/example/os:delta"}
    )

    assert image.delta_image == "quay.io/example/web:delta"
    assert image.delta_images[0].delta_image == "quay.io/example/sidecar:delta"
    serialized = ListResult(data=[image]).to_dict()["data"][0]
    assert serialized["image"] == "quay.io/example/web:1"
    assert serialized["deltaImage"] == "quay.io/example/web:delta"
    assert serialized["deltaImages"][0]["targetDigest"] == "sha256:sidecar"
    assert device_os.delta_image == "quay.io/example/os:delta"
    device_os_output = ListResult(data=[device_os]).to_dict()["data"][0]
    assert device_os_output == {
        "image": "quay.io/example/os:1",
        "deltaImage": "quay.io/example/os:delta",
    }

    rendered_device = Device.from_dict(
        {
            "apiVersion": "flightctl.io/v1beta1",
            "kind": "Device",
            "metadata": {"name": "device-1"},
            "spec": {
                "os": {
                    "image": "quay.io/example/os:1",
                    "deltaImage": "quay.io/example/os:delta",
                }
            },
        }
    )
    rendered_output = ListResult(data=[rendered_device]).to_dict()["data"][0]
    assert rendered_output["spec"]["os"]["deltaImage"] == "quay.io/example/os:delta"


def test_info_serialization_unwraps_one_of_application_models():
    device = Device.from_dict(
        {
            "apiVersion": "flightctl.io/v1beta1",
            "kind": "Device",
            "metadata": {"name": "device-1"},
            "spec": {
                "applications": [
                    {
                        "name": "web",
                        "appType": "container",
                        "image": "quay.io/example/web:1",
                        "deltaImage": "quay.io/example/web:delta",
                        "catalogItemRef": {
                            "catalog": "catalog",
                            "item": "web",
                            "version": "1.0.0",
                        },
                    }
                ]
            },
        }
    )

    application = ListResult(data=[device]).to_dict()["data"][0]["spec"][
        "applications"
    ][0]

    assert application["name"] == "web"
    assert application["deltaImage"] == "quay.io/example/web:delta"
    assert "actual_instance" not in application
    assert "one_of_schemas" not in application


def test_enrollment_pre_enrollment_is_preserved_in_info_output():
    request = EnrollmentRequest.from_dict(
        {
            "apiVersion": "flightctl.io/v1beta1",
            "kind": "EnrollmentRequest",
            "metadata": {"name": "enrollment-1"},
            "spec": {
                "csr": "-----BEGIN CERTIFICATE REQUEST-----",
                "preEnrollment": {"success": True},
            },
        }
    )

    assert request.to_dict()["spec"]["preEnrollment"] == {"success": True}


def test_fleet_rollout_delta_generation_uses_generic_resource_create(api_module):
    definition = {
        "apiVersion": "flightctl.io/v1beta1",
        "kind": "Fleet",
        "metadata": {"name": "delta-fleet"},
        "spec": {
            "rolloutPolicy": {"deltaGeneration": {"generateDelta": False}},
            "template": {
                "spec": {"os": {"image": "quay.io/example/os:1"}},
            },
        },
    }
    mock_api = MagicMock()
    mapping = API_MAPPING[ResourceType.FLEET]

    with patch.object(mapping, "api", return_value=mock_api):
        api_module.create(ResourceType.FLEET, definition)

    request = mock_api.create_fleet.call_args.args[0]
    assert isinstance(request, Fleet)
    assert request.spec.rollout_policy.delta_generation.generate_delta is False
    assert request.to_dict()["spec"]["rolloutPolicy"]["deltaGeneration"] == {
        "generateDelta": False
    }


def test_fleet_rollout_delta_generation_uses_generic_patch(api_module):
    existing_definition = {
        "apiVersion": "flightctl.io/v1beta1",
        "kind": "Fleet",
        "metadata": {"name": "delta-fleet"},
        "spec": {
            "rolloutPolicy": {"deltaGeneration": {"generateDelta": False}},
            "template": {"spec": {"os": {"image": "quay.io/example/os:1"}}},
        },
    }
    desired_definition = {
        **existing_definition,
        "spec": {
            **existing_definition["spec"],
            "rolloutPolicy": {"deltaGeneration": {"generateDelta": True}},
        },
    }
    existing = Fleet.from_dict(existing_definition)
    mock_api = MagicMock()
    mapping = API_MAPPING[ResourceType.FLEET]

    with patch.object(mapping, "api", return_value=mock_api):
        changed, _ = api_module.update(ResourceType.FLEET, existing, desired_definition)

    assert changed is True
    patch_items = [item.to_dict() for item in mock_api.patch_fleet.call_args.args[1]]
    assert patch_items == [
        {
            "op": "replace",
            "path": "/spec/rolloutPolicy/deltaGeneration/generateDelta",
            "value": True,
        }
    ]


def test_fleet_delta_generation_status_is_preserved_in_info_output():
    fleet_status = FleetStatus.from_dict(
        {"conditions": [], "deltaGeneration": {"completed": 2, "total": 3}}
    )

    assert fleet_status.to_dict()["deltaGeneration"] == {"completed": 2, "total": 3}


def test_generated_client_types_include_v14_digest_models():
    digest = ApplicationImageDigest.from_dict(
        {"image": "quay.io/example/web:1", "digest": "sha256:abc"}
    )

    assert digest.to_dict() == {
        "image": "quay.io/example/web:1",
        "digest": "sha256:abc",
    }
