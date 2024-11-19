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
from .api_client.api.repository_api import RepositoryApi
from .api_client.api.resourcesync_api import ResourcesyncApi
from .api_client.models.device import Device
from .api_client.models.fleet import Fleet
from .api_client.models.certificate_signing_request import CertificateSigningRequest
from .api_client.models.enrollment_request import EnrollmentRequest
from .api_client.models.repository import Repository
from .api_client.models.resource_sync import ResourceSync


class ResourceType(Enum):
    CSR = "CertificateSigningRequest"
    DEVICE = "Device"
    ENROLLMENT = "EnrollmentRequest"
    FLEET = "Fleet"
    REPOSITORY = "Repository"
    RESOURCE_SYNC = "ResourceSync"


@dataclass
class ApiResource:
    api: Union[DeviceApi, FleetApi, CertificatesigningrequestApi, EnrollmentrequestApi, RepositoryApi]
    model: Union[Device, Fleet, CertificateSigningRequest, EnrollmentRequest, Repository]

    get: str
    create: str
    list: str
    delete: str
    delete_all: str

    patch: Optional[str] = None


API_MAPPING = {
    ResourceType.DEVICE: ApiResource(
        api=DeviceApi,
        model=Device,
        get='read_device',
        create='create_device',
        list='list_devices',
        patch='patch_device',
        delete='delete_device',
        delete_all='delete_devices',
    ),
    ResourceType.FLEET: ApiResource(
        api=FleetApi,
        model=Fleet,
        get='read_fleet',
        create='create_fleet',
        list='list_fleets',
        patch='patch_fleet',
        delete='delete_fleet',
        delete_all='delete_fleets'
    ),
    ResourceType.CSR: ApiResource(
        api=CertificatesigningrequestApi,
        model=CertificateSigningRequest,
        get='read_certificate_signing_request',
        create='create_certificate_signing_request',
        list='list_certificate_signing_request',
        patch='patch_certificate_signing_request',
        delete='delete_certificate_signing_request',
        delete_all='delete_certificate_signing_requests',
    ),
    ResourceType.ENROLLMENT: ApiResource(
        api=EnrollmentrequestApi,
        model=EnrollmentRequest,
        get='read_enrollment_request',
        create='create_enrollment_request',
        list='list_enrollment_requests',
        delete='delete_enrollment_request',
        delete_all='delete_enrollment_requests',
    ),
    ResourceType.REPOSITORY: ApiResource(
        api=RepositoryApi,
        model=Repository,
        get='read_repository',
        create='create_repository',
        list='list_repositories',
        delete='delete_repository',
        delete_all='delete_repositories',
    ),
    ResourceType.RESOURCE_SYNC: ApiResource(
        api=ResourcesyncApi,
        model=ResourceSync,
        get='read_resource_sync',
        create='create_resource_sync',
        list='list_resource_sync',
        delete='delete_resource_sync',
        delete_all='delete_resource_syncs',
    ),
}
