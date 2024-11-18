# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Union

from .flightctl_api_client.types import Response

from .flightctl_api_client.models.certificate_signing_request import CertificateSigningRequest
from .flightctl_api_client.models.device import Device
from .flightctl_api_client.models.enrollment_request import EnrollmentRequest
from .flightctl_api_client.models.fleet import Fleet

from .flightctl_api_client.api.default import approve_certificate_signing_request, deny_certificate_signing_request
from .flightctl_api_client.api.certificatesigningrequest import create_certificate_signing_request, delete_certificate_signing_request, delete_certificate_signing_requests, read_certificate_signing_request, patch_certificate_signing_request, list_certificate_signing_requests
from .flightctl_api_client.api.device import create_device, delete_device, delete_devices, read_device, patch_device, list_devices
from .flightctl_api_client.api.enrollmentrequest import create_enrollment_request, delete_enrollment_request, delete_enrollment_requests, approve_enrollment_request, read_enrollment_request, list_enrollment_requests
from .flightctl_api_client.api.fleet import create_fleet, read_fleet, list_fleets, patch_fleet, delete_fleet, delete_fleets


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
    delete_all: Optional[Callable[..., Response]] = None

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
        delete_all=delete_certificate_signing_requests.sync_detailed,
        approve=approve_certificate_signing_request.sync_detailed,
        deny=deny_certificate_signing_request.sync_detailed
    ),
    ResourceType.DEVICE: ApiResource(
        model=Device,
        get=read_device.sync_detailed,
        list=list_devices.sync_detailed,
        patch=patch_device.sync_detailed,
        create=create_device.sync_detailed,
        delete=delete_device.sync_detailed,
        delete_all=delete_devices.sync_detailed
    ),
    ResourceType.ENROLLMENT: ApiResource(
        model=EnrollmentRequest,
        get=read_enrollment_request.sync_detailed,
        list=list_enrollment_requests.sync_detailed,
        create=create_enrollment_request.sync_detailed,
        delete=delete_enrollment_request.sync_detailed,
        delete_all=delete_enrollment_requests.sync_detailed,
        approve=approve_enrollment_request.sync_detailed,
        deny=approve_enrollment_request.sync_detailed
    ),
    ResourceType.FLEET: ApiResource(
        model=Fleet,
        get=read_fleet.sync_detailed,
        list=list_fleets.sync_detailed,
        create=create_fleet.sync_detailed,
        patch=patch_fleet.sync_detailed,
        delete=delete_fleet.sync_detailed,
        delete_all=delete_fleets.sync_detailed
    )
}
