# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from base64 import b64encode
from typing import Any, Callable, Dict, Optional

from .core import FlightctlModule
from .exceptions import FlightctlApiException

try:
    from flightctl.imagebuilder.api_client import ApiClient
    from flightctl.imagebuilder.configuration import Configuration
    from flightctl.imagebuilder.api.imagebuild_api import ImagebuildApi
    from flightctl.imagebuilder.api.imageexport_api import ImageexportApi
    from flightctl.imagebuilder.models.image_build import ImageBuild
    from flightctl.imagebuilder.models.image_export import ImageExport
    from flightctl.imagebuilder.exceptions import ApiException, NotFoundException
except ImportError as imp_exc:
    IB_CLIENT_IMPORT_ERROR = imp_exc
else:
    IB_CLIENT_IMPORT_ERROR = None


class FlightctlImageBuilderModule(FlightctlModule):
    """
    Module for interacting with the Flight Control Image Builder API.

    This is a separate service from the core Flight Control API and uses
    its own ApiClient, Configuration, and API classes.
    """

    def __init__(
        self,
        argument_spec: Dict[str, Any],
        error_callback: Optional[Any] = None,
        warn_callback: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        kwargs["supports_check_mode"] = True

        super().__init__(
            argument_spec=argument_spec,
            error_callback=error_callback,
            warn_callback=warn_callback,
            **kwargs,
        )

        if IB_CLIENT_IMPORT_ERROR:
            raise IB_CLIENT_IMPORT_ERROR

        client_config = Configuration(
            host=self.url.geturl(),
            ssl_ca_cert=self.ca_path,
        )
        client_config.verify_ssl = self.verify_ssl

        self._set_auth_headers()

        self.client = ApiClient(client_config)
        self._imagebuild_api = None
        self._imageexport_api = None

    def _set_auth_headers(self) -> None:
        if self.token:
            self.headers = {'Authorization': f'Bearer {self.token}'}
        elif self.username and self.password:
            basic_credentials = f"{self.username}:{self.password}"
            encoded = b64encode(basic_credentials.encode('utf-8')).decode('utf-8')
            self.headers = {'Authorization': f'Basic {encoded}'}
        else:
            self.headers = None

    @property
    def imagebuild_api(self) -> 'ImagebuildApi':
        if self._imagebuild_api is None:
            self._imagebuild_api = ImagebuildApi(self.client)
        return self._imagebuild_api

    @property
    def imageexport_api(self) -> 'ImageexportApi':
        if self._imageexport_api is None:
            self._imageexport_api = ImageexportApi(self.client)
        return self._imageexport_api

    def call_api(self, api_call: Callable, *args: Any, **kwargs: Any) -> Any:
        return api_call(
            *args,
            **kwargs,
            _headers=self.headers,
            _request_timeout=self.request_timeout,
        )

    # --- ImageBuild operations ---

    def get_image_build(self, name: str, with_exports: Optional[bool] = None) -> Optional[Any]:
        try:
            kwargs = {}
            if with_exports is not None:
                kwargs['with_exports'] = with_exports
            return self.call_api(self.imagebuild_api.get_image_build, name, **kwargs)
        except NotFoundException:
            return None
        except ApiException as e:
            raise FlightctlApiException(f"Unable to get ImageBuild {name}: {e}")

    def list_image_builds(
        self,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
        continue_token: Optional[str] = None,
        with_exports: Optional[bool] = None,
    ) -> Any:
        try:
            kwargs = {}
            if label_selector:
                kwargs['label_selector'] = label_selector
            if field_selector:
                kwargs['field_selector'] = field_selector
            if limit:
                kwargs['limit'] = limit
            if continue_token:
                kwargs['var_continue'] = continue_token
            if with_exports is not None:
                kwargs['with_exports'] = with_exports
            return self.call_api(self.imagebuild_api.list_image_builds, **kwargs)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to list ImageBuilds: {e}")

    def create_image_build(self, definition: Dict[str, Any]) -> Any:
        try:
            request_obj = ImageBuild.from_dict(definition)
            return self.call_api(self.imagebuild_api.create_image_build, request_obj)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to create ImageBuild: {e}")

    def delete_image_build(self, name: str) -> Any:
        try:
            return self.call_api(self.imagebuild_api.delete_image_build, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to delete ImageBuild {name}: {e}")

    def cancel_image_build(self, name: str) -> Any:
        try:
            return self.call_api(self.imagebuild_api.cancel_image_build, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to cancel ImageBuild {name}: {e}")

    def get_image_build_log(self, name: str) -> str:
        try:
            return self.call_api(self.imagebuild_api.get_image_build_log, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to get ImageBuild log for {name}: {e}")

    # --- ImageExport operations ---

    def get_image_export(self, name: str) -> Optional[Any]:
        try:
            return self.call_api(self.imageexport_api.get_image_export, name)
        except NotFoundException:
            return None
        except ApiException as e:
            raise FlightctlApiException(f"Unable to get ImageExport {name}: {e}")

    def list_image_exports(
        self,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        limit: Optional[int] = None,
        continue_token: Optional[str] = None,
    ) -> Any:
        try:
            kwargs = {}
            if label_selector:
                kwargs['label_selector'] = label_selector
            if field_selector:
                kwargs['field_selector'] = field_selector
            if limit:
                kwargs['limit'] = limit
            if continue_token:
                kwargs['var_continue'] = continue_token
            return self.call_api(self.imageexport_api.list_image_exports, **kwargs)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to list ImageExports: {e}")

    def create_image_export(self, definition: Dict[str, Any]) -> Any:
        try:
            request_obj = ImageExport.from_dict(definition)
            return self.call_api(self.imageexport_api.create_image_export, request_obj)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to create ImageExport: {e}")

    def delete_image_export(self, name: str) -> Any:
        try:
            return self.call_api(self.imageexport_api.delete_image_export, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to delete ImageExport {name}: {e}")

    def cancel_image_export(self, name: str) -> Any:
        try:
            return self.call_api(self.imageexport_api.cancel_image_export, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to cancel ImageExport {name}: {e}")

    def get_image_export_log(self, name: str) -> str:
        try:
            return self.call_api(self.imageexport_api.get_image_export_log, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to get ImageExport log for {name}: {e}")

    def download_image_export(self, name: str) -> bytearray:
        try:
            return self.call_api(self.imageexport_api.download_image_export, name)
        except ApiException as e:
            raise FlightctlApiException(f"Unable to download ImageExport {name}: {e}")
