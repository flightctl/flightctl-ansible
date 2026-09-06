from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock
from types import SimpleNamespace

from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import FlightctlException, FlightctlApiException, ValidationException
from plugins.module_utils.runner import perform_application_action, perform_approval

from flightctl.models.enrollment_request import EnrollmentRequest
from flightctl.models.certificate_signing_request import CertificateSigningRequest


@pytest.fixture
def mock_module():
    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {}
    mock_module = MagicMock()
    mock_module.get_endpoint.return_value = mock_get_response
    mock_module.check_mode = False

    # Input parameters
    mock_module.params = {
        "kind": ResourceType.ENROLLMENT.value,
        "name": "test-resource",
        "approved": True,
    }

    return mock_module


def test_perform_approval__get_endpoint_failure(mock_module):
    mock_module.get.side_effect = FlightctlApiException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to get resource: .*"):
        perform_approval(mock_module)
        mock_module.approve.assert_not_called()
        mock_module.exit_json.assert_not_called()


def test_perform_approval__approval_failure(mock_module):
    mock_module.approve.side_effect = FlightctlApiException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to approve resource: .*"):
        perform_approval(mock_module)
        mock_module.approve.assert_called()
        mock_module.exit_json.assert_not_called()


def test_perform_approval__approval_of_already_approved_enrollment_returns_early(mock_module):
    mock_approval = MagicMock()
    mock_approval.approved = True
    mock_status = MagicMock()
    mock_status.approval = mock_approval
    mock_approved_enrollment_response = MagicMock(spec=EnrollmentRequest)
    mock_approved_enrollment_response.status = mock_status
    mock_module.get.return_value = mock_approved_enrollment_response

    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)


def test_perform_approval__approval_of_already_approved_csr_returns_early(mock_module):
    mock_conditions = [MagicMock(type="Approved", status="True")]
    mock_status = MagicMock()
    mock_status.conditions = mock_conditions
    mock_csr_response = MagicMock(spec=CertificateSigningRequest)
    mock_csr_response.status = mock_status
    mock_module.get.return_value = mock_csr_response

    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)


def test_perform_approval__check_mode_does_not_call_approve(mock_module):
    mock_module.check_mode = True

    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_enrollment_approval(mock_module):
    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_enrollment_approval_with_false_value(mock_module):
    mock_module.params["approved"] = False
    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_csr_approval(mock_module):
    mock_module.params["kind"] = ResourceType.CSR.value
    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__no_kind(mock_module):
    mock_module.params["kind"] = None
    with pytest.raises(ValidationException, match="Invalid Kind None"):
        perform_approval(mock_module)


def test_perform_approval__invalid_kind(mock_module):
    mock_module.params["kind"] = "InvalidKind"
    with pytest.raises(ValidationException, match="Invalid Kind InvalidKind"):
        perform_approval(mock_module)


def test_perform_approval__no_name(mock_module):
    mock_module.params["name"] = ""
    with pytest.raises(ValidationException, match="Name must be specified"):
        perform_approval(mock_module)


def test_perform_approval__no_approval(mock_module):
    mock_module.params["approved"] = None
    with pytest.raises(ValidationException, match="Approved must be specified"):
        perform_approval(mock_module)


def _application(name, desired_state):
    return SimpleNamespace(
        actual_instance=SimpleNamespace(name=name, desired_state=desired_state)
    )


def _resource(applications, resource=ResourceType.DEVICE):
    spec = SimpleNamespace(applications=applications)
    if resource is ResourceType.FLEET:
        spec = SimpleNamespace(template=SimpleNamespace(spec=spec))
    return SimpleNamespace(spec=spec, to_dict=MagicMock(return_value={"kind": resource.value}))


@pytest.fixture
def application_module():
    module = MagicMock()
    module.check_mode = False
    module.params = {
        "kind": ResourceType.DEVICE.value,
        "name": "edge-1",
        "app_name": "workload",
        "state": "started",
    }
    return module


def test_application_action_is_idempotent_when_device_is_already_started(application_module):
    resource = _resource([_application("workload", "running")])
    application_module.get.return_value = resource

    perform_application_action(application_module)

    application_module.application_action.assert_not_called()
    application_module.exit_json.assert_called_once_with(changed=False, result=resource.to_dict())


def test_application_action_starts_device_when_its_application_is_stopped(application_module):
    existing = _resource([_application("workload", "stopped")])
    updated = _resource([_application("workload", "running")])
    application_module.get.return_value = existing
    application_module.application_action.return_value = updated

    perform_application_action(application_module)

    options = application_module.application_action.call_args.args[0]
    assert options.resource is ResourceType.DEVICE
    assert options.name == "edge-1"
    assert options.app_name == "workload"
    assert options.state == "started"
    application_module.exit_json.assert_called_once_with(changed=True, result=updated.to_dict())


def test_application_action_is_idempotent_when_device_is_already_stopped(application_module):
    application_module.params["state"] = "stopped"
    resource = _resource([_application("workload", "stopped")])
    application_module.get.return_value = resource

    perform_application_action(application_module)

    application_module.application_action.assert_not_called()
    application_module.exit_json.assert_called_once_with(changed=False, result=resource.to_dict())


def test_application_action_restarts_device_even_when_it_is_already_running(application_module):
    application_module.params["state"] = "restarted"
    existing = _resource([_application("workload", "running")])
    updated = _resource([_application("workload", "running")])
    application_module.get.return_value = existing
    application_module.application_action.return_value = updated

    perform_application_action(application_module)

    application_module.application_action.assert_called_once()
    application_module.exit_json.assert_called_once_with(changed=True, result=updated.to_dict())


def test_application_action_restarts_device_when_its_desired_state_is_unknown(application_module):
    application_module.params["state"] = "restarted"
    existing = _resource([_application("workload", None)])
    updated = _resource([_application("workload", "running")])
    application_module.get.return_value = existing
    application_module.application_action.return_value = updated

    perform_application_action(application_module)

    application_module.application_action.assert_called_once()
    application_module.exit_json.assert_called_once_with(changed=True, result=updated.to_dict())


def test_application_action_starts_fleet_when_its_application_is_stopped(application_module):
    application_module.params.update(
        {"kind": ResourceType.FLEET.value, "name": "fleet-a", "state": "started"}
    )
    existing = _resource([_application("workload", "stopped")], ResourceType.FLEET)
    updated = _resource([_application("workload", "running")], ResourceType.FLEET)
    application_module.get.return_value = existing
    application_module.application_action.return_value = updated

    perform_application_action(application_module)

    options = application_module.application_action.call_args.args[0]
    assert options.resource is ResourceType.FLEET
    assert options.state == "started"
    application_module.exit_json.assert_called_once_with(changed=True, result=updated.to_dict())


def test_application_action_handles_fleet_template_applications(application_module):
    application_module.params.update(
        {"kind": ResourceType.FLEET.value, "name": "fleet-a", "state": "stopped"}
    )
    existing = _resource([_application("workload", "running")], ResourceType.FLEET)
    updated = _resource([_application("workload", "stopped")], ResourceType.FLEET)
    application_module.get.return_value = existing
    application_module.application_action.return_value = updated

    perform_application_action(application_module)

    get_options = application_module.get.call_args.args[0]
    assert get_options.resource is ResourceType.FLEET
    assert get_options.rendered is None
    options = application_module.application_action.call_args.args[0]
    assert options.resource is ResourceType.FLEET
    assert options.state == "stopped"
    application_module.exit_json.assert_called_once_with(changed=True, result=updated.to_dict())


def test_application_action_uses_rendered_device(application_module):
    application_module.get.return_value = _resource([_application("workload", "running")])

    perform_application_action(application_module)

    get_options = application_module.get.call_args.args[0]
    assert get_options.resource is ResourceType.DEVICE
    assert get_options.rendered is True


def test_application_action_check_mode_does_not_call_api(application_module):
    application_module.check_mode = True
    existing = _resource([_application("workload", "stopped")])
    application_module.get.return_value = existing

    perform_application_action(application_module)

    application_module.application_action.assert_not_called()
    application_module.exit_json.assert_called_once_with(changed=True, result=existing.to_dict())


def test_application_restart_check_mode_does_not_call_api(application_module):
    application_module.params["state"] = "restarted"
    application_module.check_mode = True
    existing = _resource([_application("workload", "running")])
    application_module.get.return_value = existing

    perform_application_action(application_module)

    application_module.application_action.assert_not_called()
    application_module.exit_json.assert_called_once_with(changed=True, result=existing.to_dict())


def test_application_action_reads_desired_state_from_raw_resource(application_module):
    raw_resource = SimpleNamespace(
        raw={"spec": {"applications": [{"name": "workload", "desiredState": "running"}]}},
        to_dict=MagicMock(return_value={"kind": "Device"}),
    )
    application_module.get.return_value = raw_resource

    perform_application_action(application_module)

    application_module.application_action.assert_not_called()
    application_module.exit_json.assert_called_once_with(changed=False, result=raw_resource.to_dict())


def test_application_action_rejects_fleet_restart_before_reading_target(application_module):
    application_module.params.update(
        {"kind": ResourceType.FLEET.value, "name": "fleet-a", "state": "restarted"}
    )

    with pytest.raises(ValidationException, match="Restarting applications is only supported for Device"):
        perform_application_action(application_module)

    application_module.get.assert_not_called()
    application_module.application_action.assert_not_called()


def test_application_action_rejects_missing_application(application_module):
    application_module.get.return_value = _resource([_application("other-workload", "running")])

    with pytest.raises(FlightctlException, match="Application 'workload' not found on Device 'edge-1'"):
        perform_application_action(application_module)

    application_module.application_action.assert_not_called()


def test_application_action_rejects_missing_target(application_module):
    application_module.get.return_value = None

    with pytest.raises(FlightctlException, match="Device 'edge-1' not found"):
        perform_application_action(application_module)

    application_module.application_action.assert_not_called()
