# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from datetime import datetime
from base64 import b64encode
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple

from .constants import API_MAPPING, ResourceType
from .core import FlightctlModule
from .exceptions import FlightctlException, FlightctlApiException
from .options import ApprovalOptions, GetOptions
from .utils import diff_dicts, get_patch, json_patch


try:
    from flightctl import ApiClient
    from flightctl.configuration import Configuration
    from flightctl.api.enrollmentrequest_api import EnrollmentrequestApi
    from flightctl.api.certificatesigningrequest_api import CertificatesigningrequestApi
    from flightctl.exceptions import ApiException, NotFoundException
    from flightctl.models.patch_request_inner import PatchRequestInner
    from flightctl.models.enrollment_request_approval import EnrollmentRequestApproval
    from flightctl.models.list_meta import ListMeta
    from flightctl.models.condition import Condition
    from flightctl.models.condition_status import ConditionStatus
    from flightctl.models.condition_type import ConditionType
    from flightctl.models.certificate_signing_request_status import CertificateSigningRequestStatus
    from flightctl.models.device_decommission import DeviceDecommission
    from flightctl.models.device_decommission_target_type import DeviceDecommissionTargetType

except ImportError as imp_exc:
    ListMeta = None
    CLIENT_IMPORT_ERROR = imp_exc
else:
    CLIENT_IMPORT_ERROR = None


class ResourceProtocol(Protocol):
    def to_dict(self) -> Dict[str, Any]:
        return {}


class ListProtocol(Protocol):
    items: List[ResourceProtocol]
    metadata: ListMeta
    summary: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {}


@dataclass
class ListResult:
    data: List[ResourceProtocol]
    metadata: Optional[ListMeta] = None
    summary: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        res = dict(
            data=[d.to_dict() for d in self.data],
        )
        if self.metadata:
            res['metadata'] = self.metadata.to_dict()
        if self.summary:
            res['summary'] = self.summary.to_dict()
        return res


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

        if CLIENT_IMPORT_ERROR:
            raise CLIENT_IMPORT_ERROR

        client_config = Configuration(
            host=self.url.geturl(),
            ssl_ca_cert=self.ca_path,
        )
        client_config.verify_ssl = self.verify_ssl

        self.set_auth()

        self.client = ApiClient(client_config)

    def set_auth(self) -> None:
        """
        Sets auth headers for the underlying client based on set parameters.

        Prioritizes a set token if present on the module.
        """
        if self.token:
            self.headers = {'Authorization': f'Bearer {self.token}'}
        elif self.username and self.password:
            basic_credentials = f"{self.username}:{self.password}"
            encoded_credentials = b64encode(basic_credentials.encode('utf-8')).decode('utf-8')
            self.headers = {'Authorization': f'Basic {encoded_credentials}'}
        else:
            self.headers = None

    def call_api(self, api_call: Callable, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        """
        Makes a request to the api with shared args.

        Args:
            api_call (Callable): The callable function making the api request
            *args: The positional arguments that will be forwarded to api_call
            **kwargs: The keyword arguments that will be forwarded to api_call

        Returns:
            Any: The result of api_call
        """
        return api_call(
            *args,
            **kwargs,
            _headers=self.headers,
            _request_timeout=self.request_timeout,
        )

    def get(
        self, options: GetOptions,
    ) -> ResourceProtocol:
        """
        Makes an get query via the API.

        Args:
            resource (ResourceType): The API Resource Type.
            name (str): The API Resource name identifier

        Returns:
            Any: The found resoruce.

        Raises:
            FlightctlException: If the approval request fails.
        """
        api_type = API_MAPPING[options.resource]
        api_instance = api_type.api(self.client)

        if options.resource is ResourceType.DEVICE and options.rendered:
            get_call = getattr(api_instance, api_type.rendered)
        else:
            get_call = getattr(api_instance, api_type.get)

        try:
            if options.resource is ResourceType.TEMPLATE_VERSION:
                return self.call_api(get_call, options.fleet_name, options.name)
            elif options.resource is ResourceType.FLEET:
                return self.call_api(get_call, options.name, options.summary)
            else:
                return self.call_api(get_call, options.name)
        except NotFoundException:
            return None
        except ApiException as e:
            raise FlightctlApiException(f"Unable to fetch {options.resource.value} - {options.name}: {e}")

    def list(self, options: GetOptions) -> ListProtocol:
        """
        Makes an list query via the API.

        Args:
            resource (ResourceType): The API Resource Type.

        Returns:
            ListResponse: Response continaing the list of resources or an empty list if no resources are found.

        Raises:
            FlightctlException: If the approval request fails.
        """
        api_type = API_MAPPING[options.resource]
        api_instance = api_type.api(self.client)
        list_call = getattr(api_instance, api_type.list)

        try:
            if options.resource is ResourceType.TEMPLATE_VERSION:
                return self.call_api(list_call, options.fleet_name, **options.request_params)
            else:
                return self.call_api(list_call, **options.request_params)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to list {options.resource.value}: {e}")

    def get_one_or_many(
        self, options: GetOptions,
    ) -> ListResult:
        """
        Retrieves one or many resources from the API.

        Args:
            resource (ResourceType): The API Resource Type.
            name (Optional[str], optional): The resource name.
            kwargs (Any): Additional query parameters for the request.

        Returns:
            Response: The resource or list response for the queried resources.

        Raises:
            FlightctlException: If the response status is not 200 or 404.
        """
        if options.name:
            response = self.get(options)
            if not response:
                return ListResult(data=[])
            return ListResult(data=[response])
        else:
            response = self.list(options)
            return ListResult(
                data=response.items,
                metadata=response.metadata,
                summary=getattr(response, 'summary', None)
            )

    def create(
        self, resource: ResourceType, definition: Dict[str, Any]
    ) -> ResourceProtocol:
        """
        Creates a new resource in the API.

        Args:
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
            return self.call_api(create_call, request_obj)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to create {resource.value}: {e}")

    def update(
        self, resource: ResourceType, existing_obj: ResourceProtocol, definition: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Updates an existing resource.

        The update is equivalent to a PATCH that merges the existing representation of the
        object with the new definition.  If no differences are found between the existing
        representation and new definition no request is made.

        Args:
            resource(ResourceType): The type of resource to update.
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
        existing = existing_obj.to_dict()
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
                response = self.call_api(patch_call, name, patch_params)
                changed |= True
            except ApiException as e:
                raise FlightctlApiException(f"Unable to create {resource.value}: {e}")

        return changed, (response if diffs else existing_obj)

    def replace(
            self, resource: ResourceType, definition: Dict[str, Any]
    ) -> ResourceProtocol:
        """
        Replaces an existing resource.

        The replacement is equivalent to a PUT.

        Args:
            resource(ResourceType): The type of resource to replace
            definition(Dict[str, Any]): The desired state of the resource.

        Returns:
            Dict[str, Any]: The result of the replace operation.
        """
        name = definition["metadata"]["name"]
        api_type = API_MAPPING[resource]
        api_instance = api_type.api(self.client)
        replace_call = getattr(api_instance, api_type.replace)

        try:
            request_obj = api_type.model.from_dict(definition)
            return self.call_api(replace_call, name, request_obj)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to replace {resource.value}: {e}")

    def delete(self, resource: ResourceType, name: str, fleet_name: str) -> Optional[ResourceProtocol]:
        """
        Deletes resources from the API.

        Args:
            endpoint (str): The API endpoint (resource type).
            name (str): The resource name.

        Returns:
            Tuple[bool, Optional[Any]]:
                A tuple containing:
                - A boolean indicating whether the resource was deleted (changed).
                - An optional response body of the delete operation.
        """
        if not name:
            raise FlightctlApiException("A resource name must be provided for deletion.")

        api_type = API_MAPPING[resource]
        api_instance = api_type.api(self.client)
        delete_call = getattr(api_instance, api_type.delete)
        try:
            if resource is ResourceType.TEMPLATE_VERSION:
                response = self.call_api(delete_call, fleet_name, name)
            else:
                response = self.call_api(delete_call, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to delete {resource.value} - {name}: {e}")

        return response

    def approve(self, input: ApprovalOptions) -> None:
        """
        Makes an approval request via the API.

        Args:
            input (ApprovalOptions): Input containing the necessary approval data

        Raises:
            FlightctlException: If the approval request fails.
        """
        if input.resource is ResourceType.ENROLLMENT:
            # Enrollment requests require an additional body argument
            # TODO clean up the dict params -> input -> dict -> request serialization steps
            api_instance = EnrollmentrequestApi(self.client)
            body = EnrollmentRequestApproval.from_dict(input.to_request_params())
            try:
                self.call_api(api_instance.approve_enrollment_request, input.name, body)
            except ApiException as e:
                raise FlightctlApiException(f"Unable to approve {input.resource.value} - {input.name}: {e}")
        else:
            api_instance = CertificatesigningrequestApi(self.client)
            try:
                csr = self.call_api(api_instance.get_certificate_signing_request, input.name)

                if csr.status is None:
                    csr.status = CertificateSigningRequestStatus(conditions=[])

                expected_type = ConditionType.APPROVED if input.approved else ConditionType.DENIED

                # Idempotency of certificate approval/denial is no longer handled in Flight Control.
                # This logic will be enforced within the Ansible collection instead.

                if any(cond.type == expected_type for cond in csr.status.conditions):  # Check if the condition already exists
                    return csr

                approval_type = Condition(
                    type=expected_type,
                    status=ConditionStatus.TRUE,
                    observed_generation=1,
                    last_transition_time=datetime.now().isoformat() + "Z",
                    message="The request has been approved." if input.approved else "The request has been denied.",
                    reason="ManualApproval" if input.approved else "ManualDenial"
                )

                csr.status.conditions.append(approval_type)

                self.call_api(api_instance.update_certificate_signing_request_approval, input.name, csr)
            except ApiException as e:
                raise FlightctlApiException(f"Unable to approve {input.resource.value} - {input.name}: {e}")

    def decommission(self, device_name: str, definition: Dict[str, Any]) -> ResourceProtocol:
        """
        Sends a decommission request for a device.

        Args:
            device_name (str): The name of the device to decommission.

        Returns:
            ResourceProtocol: The updated device resource after decommissioning.

        Raises:
            FlightctlApiException: If the request fails.
        """
        api_type = API_MAPPING[ResourceType.DEVICE]
        api_instance = api_type.api(self.client)

        if not hasattr(api_instance, "decommission_device"):
            raise FlightctlException(f"Decommissioning is not supported for resource type {ResourceType.DEVICE}")

        decommission_call = api_instance.decommission_device

        target = definition.get("target", "Unenroll")

        try:
            target_enum = DeviceDecommissionTargetType(target)
        except ValueError:
            raise FlightctlException(f"Invalid target value: {target}. Must be 'Unenroll' or 'FactoryReset'")

        try:
            device_decommission = DeviceDecommission(target=target_enum)
            return self.call_api(decommission_call, device_name, device_decommission)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to decommission device {device_name}: {e}")
