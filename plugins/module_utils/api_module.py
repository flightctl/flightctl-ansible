# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple

from .constants import ResourceType, RESOURCE_MAPPING
from .core import FlightctlModule
from .exceptions import FlightctlException # TODO use FlightctlHTTPException
from .inputs import ApprovalInput
from .utils import diff_dicts, get_patch, json_patch

from .flightctl_api_client import AuthenticatedClient
from .flightctl_api_client.models.error import Error
from .flightctl_api_client.models.enrollment_request_approval import EnrollmentRequestApproval
from .flightctl_api_client.models.patch_request_item import PatchRequestItem
from .flightctl_api_client.api.default import approve_certificate_signing_request, deny_certificate_signing_request
from .flightctl_api_client.api.enrollmentrequest import approve_enrollment_request


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
        self, resource: ResourceType, name: Optional[str] = None,
    ) -> Optional[Any]:
        resource = RESOURCE_MAPPING[resource]
        response = resource.get(name, client=self.client)

        if isinstance(response.parsed, Error):
            if response.status_code is HTTPStatus.NOT_FOUND:
                return None
            fail_msg = f"Unable to fetch {resource.value} - {input.name}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)

        return response.parsed

    def list(self, resource: ResourceType, **kwargs: Any) -> List:
        resource = RESOURCE_MAPPING[resource]
        response = resource.list(client=self.client, **kwargs)

        if isinstance(response.parsed, Error):
            fail_msg = f"Unable to list {resource.value}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)

        return response.parsed

    def get_one_or_many(
        self, resource: ResourceType, name: Optional[str] = None, **kwargs: Any
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
            response = self.get(resource, name)
            if not response:
                return []
            return [response.to_dict()]
        else:
            res = self.list(resource, **kwargs)
            if res:
                return res.to_dict()
            return {}

    def create(
        self, resource: ResourceType, definition: Dict[str, Any]
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
        resource = RESOURCE_MAPPING[resource]
        response = resource.create(client=self.client, body=resource.model.from_dict(definition))

        if isinstance(response.parsed, Error):
            fail_msg = f"Unable to create {resource.value}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)

        return response.parsed.to_dict()

    def update(
        self, resource: ResourceType, existing: Dict[str, Any], definition: Dict[str, Any]
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

        patch = get_patch(existing, definition)
        obj, error = json_patch(existing, patch)
        if error:
            raise FlightctlException(f"There was an error with json_patch: {error}")

        match, diffs = diff_dicts(existing, obj)
        if diffs:
            patch_items = [PatchRequestItem.from_dict(p) for p in patch]

            # TODO handle some patch endpoints not existing... like enrollment requests
            # should probably branch out a patch / put method in this module...
            resource = RESOURCE_MAPPING[resource]
            response = resource.patch(name, client=self.client, body=patch_items)

            if isinstance(response.parsed, Error):
                fail_msg = f"Unable to update {resource.value}"
                if response.message:
                    fail_msg += f", message: {response.message}"
                raise FlightctlException(fail_msg)

        # TODO align on these methods returning changed or if it should just be handled by the caller?
        # The others always returned changed = True but this one may not run based on the diffs between existing and definition
        return changed, (response.json if diffs else existing)

    def delete(self, resource: ResourceType, name: str) -> Optional[Any]:
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
        resource = RESOURCE_MAPPING[resource]
        response = resource.delete(name, client=self.client)

        if isinstance(response.parsed, Error):
            if response.status_code.is_success:
                return None
            fail_msg = f"Unable to delete {resource.value} - {name}"
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
        if input.resource is ResourceType.CSR:
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
            fail_msg = f"Unable to approve {input.resource.value} for {input.name}"
            if response.message:
                fail_msg += f", message: {response.message}"
            raise FlightctlException(fail_msg)
