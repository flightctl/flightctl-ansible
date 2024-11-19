# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


from .api_client.api.device_api import DeviceApi
from .api_client.api.fleet_api import FleetApi
from .api_client.api.certificatesigningrequest_api import CertificatesigningrequestApi
from .api_client.api.enrollmentrequest_api import EnrollmentrequestApi
from .api_client.models.device import Device as Dev
from .api_client.models.fleet import Fleet as Fl
from .api_client.models.certificate_signing_request import CertificateSigningRequest as Cert
from .api_client.models.enrollment_request import EnrollmentRequest as Enroll

# TODO expand ResourceType to include additional types
class ResourceType(Enum):
    CSR = "CertificateSigningRequest"
    DEVICE = "Device"
    ENROLLMENT = "EnrollmentRequest"
    FLEET = "Fleet"


@dataclass
class ApiResource:
    api: Union[DeviceApi, FleetApi]
    model: Union[Dev, Fl]

    get: str
    create: str
    list: str
    delete: str
    delete_all: str

    patch: Optional[str] = None


API_MAPPING = {
    ResourceType.DEVICE: ApiResource(
        api=DeviceApi,
        model=Dev,
        get='read_device',
        create='create_device',
        list='list_devices',
        patch='patch_device',
        delete='delete_device',
        delete_all='delete_devices',
    ),
    ResourceType.FLEET: ApiResource(
        api=FleetApi,
        model=Fl,
        get='read_fleet',
        create='create_fleet',
        list='list_fleets',
        patch='patch_fleet',
        delete='delete_fleet',
        delete_all='delete_fleets'
    ),
    ResourceType.CSR: ApiResource(
        api=CertificatesigningrequestApi,
        model=Cert,
        get='read_certificate_signing_request',
        create='create_certificate_signing_request',
        list='list_certificate_signing_request',
        patch='patch_certificate_signing_request',
        delete='delete_certificate_signing_request',
        delete_all='delete_certificate_signing_requests',
    ),
    ResourceType.ENROLLMENT: ApiResource(
        api=EnrollmentrequestApi,
        model=Enroll,
        get='read_enrollment_request',
        create='create_enrollment_request',
        list='list_enrollment_requests',
        delete='delete_enrollment_request',
        delete_all='delete_enrollment_requests',
    ),
}
