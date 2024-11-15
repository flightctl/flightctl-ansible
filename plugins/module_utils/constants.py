# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Union

from .flightctl_api_client.types import Response
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


# TODO expand ResourceType to include additional types
class ResourceType(Enum):
    CSR = "CertificateSigningRequest"
    DEVICE = "Device"
    ENROLLMENT = "EnrollmentRequest"
    FLEET = "Fleet"


class RequestType(Enum):
    GET = "GET"
    LIST = "LIST"
    PATCH = "PATCH"
    CREATE = "CREATE"
    DELETE = "DELETE"


@dataclass
class ApiResource:
    model: Union[Device, EnrollmentRequest, CertificateSigningRequest]

    get: Optional[Callable[..., Response]] = None
    list: Optional[Callable[..., Response]] = None
    patch: Optional[Callable[..., Response]] = None
    create: Optional[Callable[..., Response]] = None
    delete: Optional[Callable[..., Response]] = None

    approve: Optional[Callable[..., Response]] = None
    deny: Optional[Callable[..., Response]] = None


RESOURCE_MAPPING = {
    ResourceType.CSR: ApiResource(
        model=CertificateSigningRequest,
        get=read_certificate_signing_request.sync_detailed,
        list=list_certificate_signing_requests.sync_detailed,
        patch=patch_certificate_signing_request.sync_detailed,
        create=create_certificate_signing_request.sync_detailed,
        delete=delete_certificate_signing_request.sync_detailed,
        approve=approve_certificate_signing_request.sync_detailed,
        deny=deny_certificate_signing_request.sync_detailed
    ),
    ResourceType.DEVICE: ApiResource(
        model=Device,
        get=read_device.sync_detailed,
        list=read_device.sync_detailed,
        patch=patch_device.sync_detailed,
        create=create_device.sync_detailed,
        delete=delete_device.sync_detailed
    ),
    ResourceType.ENROLLMENT: ApiResource(
        model=EnrollmentRequest,
        get=read_enrollment_request.sync_detailed,
        list=list_enrollment_requests.sync_detailed,
        create=create_enrollment_request.sync_detailed,
        delete=delete_enrollment_request.sync_detailed,
        approve=approve_enrollment_request.sync_detailed,
        deny=approve_enrollment_request.sync_detailed
    ),
}
