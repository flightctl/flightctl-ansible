# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import ParseResult

from ansible.module_utils.six.moves.http_cookiejar import CookieJar
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import (ConnectionError, Request,
                                       SSLValidationError)

from .constants import Kind
from .core import FlightctlModule
from .exceptions import FlightctlException, FlightctlHTTPException
from .inputs import ApprovalInput
from .utils import diff_dicts, get_patch, json_patch

from .flightctl_api_client import Client
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

class Response:
    """
    Represents an HTTP response.

    Attributes:
        status (int): The HTTP status code of the response.
        data (Any): The response data (raw content).
        headers (Optional[Any]): The response headers, converted to lowercase keys.
    """

    def __init__(self, status: int, data: Any, headers: Optional[Any] = None) -> None:
        """
        Initializes the Response object.

        Args:
            status (int): The HTTP status code.
            data (Any): The response data.
            headers (Optional[Any], optional): The response headers.
        """
        self.status = status
        self.data = data
        # [('h1', 'v1'), ('H2', 'V2')] -> {'h1': 'v1', 'h2': 'V2'}
        self.headers = (
            dict((k.lower(), v) for k, v in dict(headers).items()) if headers else {}
        )

        self._json = None

    @property
    def json(self) -> Any:
        """
        Returns the response data as JSON, if possible.

        Returns:
            Any: The parsed JSON data.

        Raises:
            FlightctlHTTPException: If the data is not valid JSON.
        """
        if self._json is None:
            try:
                self._json = json.loads(self.data)
            except ValueError as value_exp:
                raise FlightctlHTTPException(
                    f"Received invalid JSON response: {self.data}"
                ) from value_exp
        return self._json


class FlightctlAPIModule(FlightctlModule):
    """
    API module for interacting with the Flightctl API.

    Inherits from FlightctlModule and provides methods to perform API requests
    like GET, POST, PATCH, and DELETE.

    Attributes:
        API_ENDPOINTS (dict): Mapping of resource types to API endpoints.
    """

    API_ENDPOINTS: Dict[str, str] = {
        "fleet": "/api/v1/fleets",
        "resourcesync": "/api/v1/resourcesyncs",
        "device": "/api/v1/devices",
        "repository": "/api/v1/repositories",
        "enrollmentrequest": "api/v1/enrollmentrequests",
        "certificatesigningrequest": "api/v1/certificatesigningrequests"
    }

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

        self.session = Request(
            cookies=CookieJar(),
            timeout=self.request_timeout,
            validate_certs=self.verify_ssl,
            ca_path=self.ca_path,
        )

        self.client = Client(
            base_url=self.url.geturl(),
            verify_ssl=self.verify_ssl,
        )

    @staticmethod
    def normalize_endpoint(endpoint: str) -> Optional[str]:
        """
        Normalizes the endpoint by converting it to lowercase.

        Args:
            endpoint (str): The API endpoint.

        Returns:
            Union[str, None]: The normalized endpoint or None if the input is invalid.
        """
        return endpoint.lower() if endpoint else None

    def get_endpoint(
        self, endpoint: str, name: Optional[str] = None, **kwargs: Any
    ) -> Response:
        """
        Sends a GET request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint (resource type).
            name (Optional[str], optional): The resource name (optional).

        Returns:
            Response: The response object.
        """
        url = self.build_url(endpoint, name, query_params=kwargs)
        return self.request("GET", url.geturl(), **kwargs)

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


    def patch_endpoint(
        self, endpoint: str, name: str, patch: List[Dict[str, Any]]
    ) -> Response:
        """
        Sends a PATCH request to the specified endpoint with a JSON patch.

        Args:
            endpoint (str): The API endpoint (resource type) to patch.
            name (str): The resource name to patch.
            patch (List[Dict[str, Any]]): The patch data (list of patch operations).

        Returns:
            Response: The response object.
        """
        url = self.build_url(endpoint, name)
        return self.request("PATCH", url.geturl(), patch=patch)

    def post_endpoint(self, endpoint: str, **kwargs: Any) -> Response:
        """
        Sends a POST request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint (resource type).
            **kwargs (Any): Additional parameters for the request.

        Returns:
            Response: The response object.
        """
        url = self.build_url(endpoint, None)
        self.warn("URL IN POST")
        self.warn(url.geturl())
        return self.request("POST", url.geturl(), **kwargs)

    def build_url(
        self,
        endpoint: str,
        name: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Constructs the full URL for an API request.

        Args:
            endpoint (str): The API endpoint (resource type).
            name (Optional[str], optional): The resource name.
            query_params (Optional[Dict[str, Any]], optional): Query parameters for the URL.

        Returns:
            ParseResult: The complete URL with the path and query parameters.

        Raises:
            FlightctlException: If the endpoint is invalid.
        """
        normalized_endpoint = self.normalize_endpoint(endpoint)
        if not normalized_endpoint or normalized_endpoint not in self.API_ENDPOINTS:
            raise FlightctlException(f"Invalid 'kind' specified: {endpoint}")

        api_endpoint = self.API_ENDPOINTS[normalized_endpoint]

        # Construct the full path
        if name:
            base_path = f"{self.url_prefix.rstrip('/')}{api_endpoint}/{name}"
        else:
            base_path = f"{self.url_prefix.rstrip('/')}{api_endpoint}"

        # Update the URL path with the base path
        url = self.url._replace(path=base_path)

        # Append query parameters if provided
        if query_params:
            # Encode the query parameters and append to the URL
            query_string = urlencode(query_params, doseq=True)
            url = url._replace(query=query_string)

        return url

    def request(
        self,
        method: str,
        url: str,
        patch: Optional[Any] = None,
        **kwargs: Any,
    ) -> Response:
        """
        Builds and sends an HTTP request.

        Args:
            method (str): The HTTP method (GET, POST, PATCH, DELETE, etc.).
            url (str): The URL for the request.
            patch (Optional[Any], optional): The patch data for PATCH requests.
            kwargs (Any): Additional parameters for the request.

        Returns:
            Response: The response object.

        Raises:
            FlightctlHTTPException: If the method is not defined or there are request errors.
        """
        if not method:
            raise FlightctlHTTPException("The HTTP method must be defined")

        # Extract the headers, this will be used in a couple of places
        headers = kwargs.get("headers", {})

        # # Authenticate to Flight Control service (if we don't have a token and if not already done so)
        # if not self.token and not self.authenticated:
        #     # This method will set a cookie in the cookie jar for us and also an token
        #     self.authenticate(**kwargs)

        if self.token:
            # If we have a token, we just use a bearer header
            headers["Authorization"] = f"Bearer {self.token}"

        if method == "PATCH":
            headers.setdefault("Content-Type", "application/json-patch+json")
            kwargs["headers"] = headers
            data = json.dumps(patch)
        elif method in ["POST", "PUT"]:
            headers.setdefault("Content-Type", "application/json")
            kwargs["headers"] = headers
            data = json.dumps(kwargs)
        else:
            data = None  # Important, if content type is not JSON, this should not be dict type

        return self._request(method, url, data=data, headers=headers)

    def _request(
        self,
        method: str,
        url: ParseResult,
        data: Optional[str] = None,
        headers: Optional[str] = None,
    ) -> Response:
        """
        Sends a raw HTTP request using the session object.

        Args:
            method (str): The HTTP method (GET, POST, etc.).
            url (str): The URL for the request.
            data (Optional[str], optional): The request body data.
            headers (Optional[str], optional): The request headers.

        Returns:
            Response: The response object.

        Raises:
            FlightctlHTTPException: If there are SSL, connection, or HTTP errors.
        """
        try:
            raw_resp = self.session.open(
                method,
                url,
                headers=headers,
                timeout=self.request_timeout,
                validate_certs=self.verify_ssl,
                follow_redirects=True,
                data=data,
            )
        except SSLValidationError as ssl_err:
            raise FlightctlHTTPException(
                f"Could not establish a secure connection to your host ({ssl_err}): {url.netloc}."
            ) from ssl_err
        except ConnectionError as con_err:
            raise FlightctlHTTPException(
                f"There was a network error of some kind trying to connect to your host ({con_err}): {url.netloc}."
            ) from con_err
        except HTTPError as http_err:
            if http_err.code >= 500:
                raise FlightctlHTTPException(
                    f"The host sent back a server error ({http_err}): {url}. Please check the logs and try again."
                ) from http_err
            elif http_err.code == 401:
                raise FlightctlHTTPException(
                    f"Invalid authentication credentials for {url} (HTTP 401)."
                ) from http_err
            elif http_err.code == 403:
                raise FlightctlHTTPException(
                    f"You don't have permission to {method} to {url} (HTTP 403)."
                ) from http_err
            elif http_err.code == 404:
                # raise FlightctlHTTPException(f"The requested object could not be found at {url.path}.") from http_err
                return Response(http_err.code, b"{}")
            elif http_err.code == 405:
                raise FlightctlHTTPException(
                    f"Cannot make a request with the {method} method to this endpoint {url}."
                ) from http_err
            elif http_err.code == 204 and method == "DELETE":
                # A 204 is a normal response for a delete function
                pass
            else:
                raise FlightctlHTTPException(
                    f"Unexpected return code when calling {url}: {http_err}."
                ) from http_err
        except Exception as e:
            raise FlightctlHTTPException(
                f"There was an unknown error when trying to connect to {url}: {type(e).__name__} {e}."
            ) from e

        return Response(raw_resp.status, raw_resp.read(), raw_resp.headers)

    def authenticate(self, **kwargs):
        # self.authenticated = True
        pass

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
    ) -> List:
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
            return self.list(kind, **kwargs).to_dict()

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
