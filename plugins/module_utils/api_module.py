# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple

from .constants import Kind
from .core import FlightctlModule
from .exceptions import FlightctlException # TODO use FlightctlHTTPException
from .inputs import ApprovalInput
from .utils import diff_dicts, get_patch, json_patch

from .flightctl_api_client import AuthenticatedClient
from .flightctl_api_client.models.device import Device
from .flightctl_api_client.models.enrollment_request import EnrollmentRequest
from .flightctl_api_client.models.certificate_signing_request import CertificateSigningRequest
from .flightctl_api_client.models.error import Error
from .flightctl_api_client.models.enrollment_request_approval import EnrollmentRequestApproval
from .flightctl_api_client.models.patch_request_item import PatchRequestItem
from .flightctl_api_client.api.default import approve_certificate_signing_request, deny_certificate_signing_request
from .flightctl_api_client.api.device import create_device, delete_device, read_device, patch_device, list_devices
from .flightctl_api_client.api.certificatesigningrequest import create_certificate_signing_request, delete_certificate_signing_request, read_certificate_signing_request, patch_certificate_signing_request, list_certificate_signing_requests
from .flightctl_api_client.api.enrollmentrequest import create_enrollment_request, delete_enrollment_request, approve_enrollment_request, read_enrollment_request, list_enrollment_requests


class FlightctlAPIModule(FlightctlModule):
    """
    API module for interacting with the Flightctl API.

    Inherits from FlightctlModule and provides methods to perform API requests
    like GET, POST, PATCH, and DELETE.
    """

    def __init__(
        self,
        argument_spec: Dict[str, Any],
        error_callback: Optional[Any] = None,
        warn_callback: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the FlightctlAPIModule.

        Args:
            argument_spec (Dict[str, Any]): The argument specification for the module.
            error_callback (Optional[Any], optional): A callback function for errors.
            warn_callback (Optional[Any], optional): A callback function for warnings.
            **kwargs (Any): Additional keyword arguments.
        """
        kwargs["supports_check_mode"] = True

        super().__init__(
            argument_spec=argument_spec,
            error_callback=error_callback,
            warn_callback=warn_callback,
            **kwargs,
        )

        self.client = AuthenticatedClient(
            base_url=self.url.geturl(),
            verify_ssl=self.verify_ssl,
            raise_on_unexpected_status=True,
            token=self.token,
            httpx_args=dict(
                cert=self.ca_path,
            )
        )

    def get(
        self, kind: Kind, name: Optional[str] = None,
    ) -> Optional[Any]:
        if kind is Kind.DEVICE:
            response = read_device.sync_detailed(name, client=self.client)
        elif kind is Kind.ENROLLMENT:
            response = read_enrollment_request.sync_detailed(name, client=self.client)
        else:
            response = read_certificate_signing_request.sync_detailed(name, client=self.client)

        if isinstance(response.parsed, Error):
            if response.status_code is HTTPStatus.NOT_FOUND:
                return None
            fail_msg = f"Unable to fetch {kind.value} - {input.name}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)

        return response.parsed

    def list(self, kind: Kind, **kwargs: Any) -> List:
        if kind is Kind.DEVICE:
            response = list_devices.sync_detailed(client=self.client, **kwargs)
        elif kind is Kind.ENROLLMENT:
            response = list_enrollment_requests.sync_detailed(client=self.client, **kwargs)
        else:
            response = list_certificate_signing_requests.sync_detailed(client=self.client, **kwargs)

        if isinstance(response.parsed, Error):
            fail_msg = f"Unable to list {kind.value}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)

        return response.parsed

    def get_one_or_many(
        self, kind: Kind, name: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """
        Retrieves one or many resources from the API.

        Args:
            endpoint (str): The API endpoint (resource type).
            name (Optional[str], optional): The resource name.
            kwargs (Any): Additional query parameters for the request.

        Returns:
            List: The list of resources or an empty list if not found.

        Raises:
            FlightctlException: If the response status is not 200 or 404.
        """
        if name:
            response = self.get(kind, name)
            if not response:
                return []
            return [response.to_dict()]
        else:
            res = self.list(kind, **kwargs)
            if res:
                return res.to_dict()
            return {}

    def create(
        self, kind: Kind, definition: Dict[str, Any]
    ) -> Any:
        """
        Creates a new resource in the API.

        Args:s
            definition (Dict[str, Any]): The resource definition.

        Returns:
            Returns:
            Tuple[bool, Dict[str, Any]]:
                A tuple containing:
                    - A boolean indicating whether the resource was created (changed).
                    - The created resource as a dictionary.
        Raises:
            FlightctlException: If the creation fails.
        """
        # TODO Dicts / structs for looking up resource -> methods
        if kind is Kind.DEVICE:
            # TODO cleaner passing around of data / figure out what types we want where and when we
            # should represent resources as their types or dicts...
            d = Device.from_dict(definition)
            response = create_device.sync_detailed(client=self.client, body=d)
        elif kind is Kind.ENROLLMENT:
            e = EnrollmentRequest.from_dict(definition)
            response = create_enrollment_request.sync_detailed(client=self.client, body=e)
        else:
            c = CertificateSigningRequest.from_dict(definition)
            response = create_certificate_signing_request.sync_detailed(client=self.client, body=c)

        # TODO share request response handling?
        if isinstance(response.parsed, Error):
            fail_msg = f"Unable to create {kind.value}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)

        return response.parsed.to_dict()

    def update(
        self, kind: Kind, existing: Dict[str, Any], definition: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        TODO - update the docstrings for modified methods

        Updates an existing resource in the API.

        Args:
            existing (Dict[str, Any]): The current state of the resource.
            definition (Dict[str, Any]): The desired state of the resource.

        Returns:
            Tuple[bool, Dict[str, Any]]:
                - A boolean indicating whether the resource was updated (changed).
                - The updated resource as a dictionary if changes were made, otherwise the unchanged existing resource.

        Raises:
            FlightctlException: If the update fails or there are errors with the patch.
        """
        changed: bool = False
        name = existing["metadata"]["name"]

        # TODO put this below calcing diffs so we can short circuit?
        patch = get_patch(existing, definition)
        obj, error = json_patch(existing, patch)
        if error:
            raise FlightctlException(f"There was an error with json_patch: {error}")

        match, diffs = diff_dicts(existing, obj)
        if diffs:
            patch_items = [PatchRequestItem.from_dict(p) for p in patch]
            if kind is Kind.DEVICE:
                response = patch_device.sync_detailed(name, client=self.client, body=patch_items)
            elif kind is Kind.ENROLLMENT:
                # TODO handle some patch endpoints not existing... like enrollment requests
                raise Exception("OH NO!")
            else:
                response = patch_certificate_signing_request.sync_detailed(name, client=self.client, body=patch_items)

            if isinstance(response.parsed, Error):
                fail_msg = f"Unable to update {kind.value}"
                if response.message:
                    fail_msg += f", message: {response.message}"
                raise FlightctlException(fail_msg)

        # TODO align on these methods returning changed or if it should just be handled by the caller?
        # The others always returned changed = True but this one may not run based on the diffs between existing and definition
        return changed, (response.json if diffs else existing)

    def delete(self, kind: Kind, name: str) -> Optional[Any]:
        """
        Deletes a resource from the API.

        Args:
            endpoint (str): The API endpoint (resource type).
            name (str): The resource name.

        Returns:
            Tuple[bool, Optional[Any]]:
                A tuple containing:
                - A boolean indicating whether the resource was deleted (changed).
                - An optional response body of the delete operation.
        """
        if kind is Kind.DEVICE:
            response = delete_device.sync_detailed(name, client=self.client)
        elif kind is Kind.ENROLLMENT:
            response = delete_enrollment_request.sync_detailed(name, client=self.client)
        else:
            response = delete_certificate_signing_request.sync_detailed(name, client=self.client)

        if isinstance(response.parsed, Error):
            if response.status_code.is_success:
                return None
            fail_msg = f"Unable to delete {kind.value} - {name}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)

        return response.parsed

    def approve(self, input: ApprovalInput) -> None:
        """
        Makes an approval request via the API.

        Args:
            input (ApprovalInput): Input containing the necessary approval data

        Raises:
            FlightctlException: If the approval request fails.
        """
        if input.kind is Kind.CSR:
            # CSR requests are approved / denied by hitting separate endpoints
            if input.approved :
                response = approve_certificate_signing_request.sync(input.name, client=self.client)
            else:
                response = deny_certificate_signing_request.sync(input.name, client=self.client)
        else:
            # Enrollment requests are approved / denied by hitting the same endpoint with different vlaues
            # TODO not this
            d = input.to_request_params()
            b = EnrollmentRequestApproval.from_dict(d)
            response = approve_enrollment_request.sync(input.name, client=self.client, body=b)

        if isinstance(response, Error):
            fail_msg = f"Unable to approve {input.kind.value} for {input.name}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)
