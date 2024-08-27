#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.urls import Request, SSLValidationError, ConnectionError
from ansible.module_utils.six.moves.http_cookiejar import CookieJar
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.six.moves.urllib.error import HTTPError

from .exceptions import FlightctlException, FlightctlHTTPException
from .core import FlightctlModule

from typing import Any, Dict, List, Optional, Union

class Response:
    def __init__(self, status: int, data: Any,  headers: Optional[Any] = None) -> None:
        self.status = status
        self.data = data
        # [('h1', 'v1'), ('H2', 'V2')] -> {'h1': 'v1', 'h2': 'V2'}
        self.headers = (
            dict((k.lower(), v) for k, v in dict(headers).items()) if headers else {}
        )

        self._json = None

    @property
    def json(self) -> Any:
        if self._json is None:
            try:
                self._json = json.loads(self.data)
            except ValueError as value_exp:
                raise FlightctlHTTPException(
                    f"Received invalid JSON response: {self.data}"
                ) from value_exp
        return self._json


class FlightctlAPIModule(FlightctlModule):
    IDENTITY_FIELDS = {"users": "username"}
    ENCRYPTED_STRING = "$encrypted$"
    API_ENDPOINTS = {
        'fleet': '/api/v1/fleets',
        'resourcesync': '/api/v1/resourcesyncs',
        'device': '/api/v1/devices',
        'repository': '/api/v1/repositories',
    }

    def __init__(self, argument_spec : Dict[str, Any], error_callback: Optional[Any] = None, warn_callback: Optional[Any] = None, **kwargs: Any) -> None:
        kwargs['supports_check_mode'] = True
        super().__init__(argument_spec=argument_spec, error_callback=error_callback, warn_callback=warn_callback, **kwargs)
        self.session = Request(cookies=CookieJar(), timeout=self.request_timeout, validate_certs=self.verify_ssl)

    @staticmethod
    def normalize_endpoint(endpoint: str) -> Union[str, None]:
        return endpoint.lower() if endpoint else None

    def get_endpoint(self, endpoint: str, name: Optional[str] = None, **kwargs: Any):
        return self.request('GET', endpoint, name, **kwargs)

    def patch_endpoint(self, endpoint: str, name: str, **kwargs: Any):
        return self.request('PATCH', endpoint, name, **kwargs)

    def post_endpoint(self, endpoint: str, **kwargs: Any):
        return self.request('POST', endpoint, **kwargs)

    def delete_endpoint(self, endpoint: str, name: str, **kwargs: Any):
        return self.request('DELETE', endpoint, name, **kwargs)

    def build_url(self, endpoint:str, name: Optional[str] = None, query_params: Optional[Any] = None):
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

    def request(self, method: str, endpoint: str, name: Optional[str] = None, **kwargs: Any):
        # In case someone is calling us directly; make sure we were given a method, let's not just assume a GET
        if not method:
            raise FlightctlHTTPException("The HTTP method must be defined")

        if method in ['POST', 'PUT', 'PATCH']:
            url = self.build_url(endpoint, name)
        else:
            url = self.build_url(endpoint, name, query_params=kwargs)

        # Extract the headers, this will be used in a couple of places
        headers = kwargs.get('headers', {})

        # # Authenticate to Flight Control service (if we don't have a token and if not already done so)
        # if not self.token and not self.authenticated:
        #     # This method will set a cookie in the cookie jar for us and also an token
        #     self.authenticate(**kwargs)

        if self.token:
            # If we have a token, we just use a bearer header
            headers['Authorization'] = 'Bearer {0}'.format(self.token)

        if method == ["PATCH"]:
            headers.setdefault('Content-Type', 'application/json-patch+json')
            kwargs['headers'] = headers

        if method in ['POST', 'PUT']:
            headers.setdefault('Content-Type', 'application/json')
            kwargs['headers'] = headers

        data = None  # Important, if content type is not JSON, this should not be dict type

        if headers.get('Content-Type', '') == 'application/json':
            data = json.dumps(kwargs)

        return self._request(method, url, data=data, headers=headers)

    def _request(self, method: str, url, data: Optional[str] = None, headers: Optional[str] = None):

        try:
            raw_resp = self.session.open(
                method,
                url.geturl(),
                headers=headers,
                timeout=self.request_timeout,
                validate_certs=self.verify_ssl,
                follow_redirects=True,
                data=data
            )
        except SSLValidationError as ssl_err:
            raise FlightctlHTTPException(f"Could not establish a secure connection to your host ({ssl_err}): {url.netloc}.") from ssl_err
        except ConnectionError as con_err:
            raise FlightctlHTTPException(f"There was a network error of some kind trying to connect to your host ({con_err}): {url.netloc}.") from con_err
        except HTTPError as http_err:
            if http_err.code >= 500:
                raise FlightctlHTTPException(f"The host sent back a server error ({http_err}): {url.path}. Please check the logs and try again later.") from http_err
            elif http_err.code == 401:
                raise FlightctlHTTPException(f"Invalid authentication credentials for {url.path} (HTTP 401).") from http_err
            elif http_err.code == 403:
                raise FlightctlHTTPException(f"You don't have permission to {method} to {url.path} (HTTP 403).") from http_err
            elif http_err.code == 404:
                # raise FlightctlHTTPException(f"The requested object could not be found at {url.path}.") from http_err
                return Response(http_err.code, b'{}')
            elif http_err.code == 405:
                raise FlightctlHTTPException(f"Cannot make a request with the {method} method to this endpoint {url.path}.") from http_err
            elif http_err.code == 204 and method == 'DELETE':
                # A 204 is a normal response for a delete function
                pass
            else:
                raise FlightctlHTTPException(f"Unexpected return code when calling {url.geturl()}: {http_err}.") from http_err
        except (Exception) as e:
            raise FlightctlHTTPException(f"There was an unknown error when trying to connect to {url.geturl()}: {type(e).__name__} {e}.") from e

        return Response(raw_resp.status, raw_resp.read(), raw_resp.headers)

    def authenticate(self, **kwargs):
        # self.authenticated = True
        pass

    def get_one_or_many(self, endpoint: str, name: Optional[str] = None, **kwargs: Any) -> List:
        response = self.get_endpoint(endpoint, name, **kwargs)
        if response.status not in [200, 404]:
            fail_msg = f"Got a {response.status} when trying to get {endpoint}"
            if "message" in response.json:
                fail_msg += f", message: {response.json['message']}"
            raise FlightctlException(fail_msg)

        if response.status == 404:
            # Resource not found
            return []

        if response.json and response.json.get("items") is not None:
            return response.json["items"] if len(response.json.get("items")) > 0 else []

        return [response.json]

    def create(self, params: Dict[str, Any], definition: Dict[str, Any]):
        response = self.post_endpoint(params.get('kind'), **definition)
        if response.status == 201:
            return response.json
        else:
            msg = f"Unable to create {params.get('kind')} {params.get('name')}: {response.status}"
            raise FlightctlException(msg)

    def update(self):
        pass

    def delete(self, endpoint: str, name: str):
        response = self.delete_endpoint(endpoint, name)
        if response.status == 200:
            return response.json
        else:
            msg = f"Unable to delete {endpoint} {name}: {response.status}"
            raise FlightctlException(msg)
