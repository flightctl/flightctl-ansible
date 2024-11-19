# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Any, Dict, List, Optional, Tuple

from .constants import API_MAPPING, ResourceType
from .core import FlightctlModule
from .exceptions import FlightctlException, FlightctlApiException
from .inputs import ApprovalInput
from .utils import diff_dicts, get_patch, json_patch

from .api_client.api_client import ApiClient
from .api_client.configuration import Configuration
from .api_client.api.enrollmentrequest_api import EnrollmentrequestApi
from .api_client.api.default_api import DefaultApi
from .api_client.exceptions import ApiException, NotFoundException
from .api_client.models.patch_request_inner import PatchRequestInner
from .api_client.models.enrollment_request_approval import EnrollmentRequestApproval


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

        client_config = Configuration(
            host=self.url.geturl(),
            ssl_ca_cert=self.ca_path,
            access_token=self.token,
        )
        client_config.verify_ssl = self.verify_ssl

        self.client = ApiClient(client_config)

    def get(
        self, resource: ResourceType, name: Optional[str] = None,
    ) -> Optional[Any]:
        api_type = API_MAPPING[resource]
        api_instance = api_type.api(self.client)
        get_call = getattr(api_instance, api_type.get)

        try:
            return get_call(name)
        except NotFoundException:
            return None
        except ApiException as e:
            raise FlightctlApiException(f"Unable to fetch {resource.value} - {name}: {e}")


    def list(self, resource: ResourceType, **kwargs: Any) -> List:
        api_type = API_MAPPING[resource]
        api_instance = api_type.api(self.client)
        list_call = getattr(api_instance, api_type.list)

        try:
            return list_call(**kwargs)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to list {resource.value}: {e}")

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
            return response.to_dict()
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
        api_type = API_MAPPING[resource]
        api_instance = api_type.api(self.client)
        create_call = getattr(api_instance, api_type.create)

        try:
            request_obj = api_type.model.from_dict(definition)
            return create_call(request_obj).to_dict()
        except ApiException as e:
            raise FlightctlApiException(f"Unable to create {resource.value}: {e}")

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
            api_type = API_MAPPING[resource]
            api_instance = api_type.api(self.client)
            patch_call = getattr(api_instance, api_type.patch)

            try:
                patch_params = [PatchRequestInner.from_dict(p) for p in patch]
                response = patch_call(name, patch_params).to_dict()
            except ApiException as e:
                raise FlightctlApiException(f"Unable to create {resource.value}: {e}")

        # TODO align on these methods returning changed or if it should just be handled by the caller?
        # The others always returned changed = True but this one may not run based on the diffs between existing and definition
        return changed, (response if diffs else existing)

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
        api_type = API_MAPPING[resource]
        api_instance = api_type.api(self.client)

        if name:
            delete_call = getattr(api_instance, api_type.delete)
            try:
                response = delete_call(name)
            except ApiException as e:
                raise FlightctlApiException(f"Unable to delete {resource.value} - {name}: {e}")
        else:
            delete_call = getattr(api_instance, api_type.delete_all)
            try:
                response = delete_call()
            except ApiException as e:
                raise FlightctlApiException(f"Unable to delete {resource.value} - {name}: {e}")

        return response.to_dict()

    def approve(self, input: ApprovalInput) -> None:
        """
        Makes an approval request via the API.

        Args:
            input (ApprovalInput): Input containing the necessary approval data

        Raises:
            FlightctlException: If the approval request fails.
        """
        if input.resource is ResourceType.ENROLLMENT:
            # Enrollment requests require an additional body argument
            # TODO clean up the dict params -> input -> dict -> request serialization steps
            api_instance = EnrollmentrequestApi(self.client)
            body = EnrollmentRequestApproval.from_dict(input.to_request_params())
            try:
                api_instance.approve_enrollment_request(input.name, body)
            except ApiException as e:
                raise FlightctlApiException(f"Unable to approve {input.resource.value} - {input.name}: {e}")
        else:
            api_instance = DefaultApi(self.client)
            try:
                if input.approved:
                    api_instance.approve_certificate_signing_request(input.name)
                else:
                    api_instance.deny_certificate_signing_request(input.name)
            except ApiException as e:
                raise FlightctlApiException(f"Unable to approve {input.resource.value} - {input.name}: {e}")
