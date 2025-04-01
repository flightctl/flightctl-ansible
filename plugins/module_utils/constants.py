# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class ResourceType(Enum):
    CSR = "CertificateSigningRequest"
    DEVICE = "Device"
    ENROLLMENT = "EnrollmentRequest"
    FLEET = "Fleet"
    REPOSITORY = "Repository"
    RESOURCE_SYNC = "ResourceSync"
    TEMPLATE_VERSION = "TemplateVersion"
    ENROLLMENT_CONFIG = "EnrollmentConfig"


API_MAPPING = {}


try:
    # Apis
    from flightctl.api.device_api import DeviceApi
    from flightctl.api.fleet_api import FleetApi
    from flightctl.api.certificatesigningrequest_api import CertificatesigningrequestApi
    from flightctl.api.enrollmentrequest_api import EnrollmentrequestApi
    from flightctl.api.repository_api import RepositoryApi
    from flightctl.api.resourcesync_api import ResourcesyncApi

    # Models
    from flightctl.models.device import Device
    from flightctl.models.fleet import Fleet
    from flightctl.models.certificate_signing_request import CertificateSigningRequest
    from flightctl.models.enrollment_request import EnrollmentRequest
    from flightctl.models.repository import Repository
    from flightctl.models.resource_sync import ResourceSync
    from flightctl.models.enrollment_config import EnrollmentConfig

    @dataclass
    class ApiResource:
        api: Union[DeviceApi, FleetApi, CertificatesigningrequestApi, EnrollmentrequestApi, RepositoryApi, ResourcesyncApi]
        model: Union[Device, Fleet, CertificateSigningRequest, EnrollmentRequest, Repository, ResourceSync, EnrollmentConfig]

        get: str

        create: Optional[str] = None
        list: Optional[str] = None
        delete: Optional[str] = None
        delete_all: Optional[str] = None
        patch: Optional[str] = None
        replace: Optional[str] = None
        rendered: Optional[str] = None
        decommission: Optional[str] = None

    API_MAPPING = {
        ResourceType.DEVICE: ApiResource(
            api=DeviceApi,
            model=Device,
            get='read_device',
            create='create_device',
            list='list_devices',
            patch='patch_device',
            replace='replace_device',
            delete='delete_device',
            delete_all='delete_devices',
            rendered='get_rendered_device',
            decommission='decommission_device'

        ),
        ResourceType.FLEET: ApiResource(
            api=FleetApi,
            model=Fleet,
            get='read_fleet',
            create='create_fleet',
            list='list_fleets',
            patch='patch_fleet',
            replace='replace_fleet',
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
            replace='replace_certificate_signing_request',
            delete='delete_certificate_signing_request',
            delete_all='delete_certificate_signing_requests',
        ),
        ResourceType.ENROLLMENT: ApiResource(
            api=EnrollmentrequestApi,
            model=EnrollmentRequest,
            get='read_enrollment_request',
            create='create_enrollment_request',
            list='list_enrollment_requests',
            replace='replace_enrollment_request',
            delete='delete_enrollment_request',
            delete_all='delete_enrollment_requests',
        ),
        ResourceType.REPOSITORY: ApiResource(
            api=RepositoryApi,
            model=Repository,
            get='read_repository',
            create='create_repository',
            list='list_repositories',
            patch='patch_repository',
            replace='replace_repository',
            delete='delete_repository',
            delete_all='delete_repositories',
        ),
        ResourceType.RESOURCE_SYNC: ApiResource(
            api=ResourcesyncApi,
            model=ResourceSync,
            get='read_resource_sync',
            create='create_resource_sync',
            list='list_resource_sync',
            patch='patch_resource_sync',
            replace='replace_resource_sync',
            delete='delete_resource_sync',
            delete_all='delete_resource_syncs',
        ),
        ResourceType.ENROLLMENT_CONFIG: ApiResource(
            api=EnrollmentrequestApi,
            model=EnrollmentConfig,
            get='get_enrollment_config'
        )
    }
except ImportError as imp_exc:
    # Handled elsewhere
    pass
