# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class ResourceType(Enum):
    AUTH_PROVIDER = "AuthProvider"
    CATALOG = "Catalog"
    CATALOG_ITEM = "CatalogItem"
    CSR = "CertificateSigningRequest"
    DEVICE = "Device"
    ENROLLMENT = "EnrollmentRequest"
    EVENT = "Event"
    FLEET = "Fleet"
    ORGANIZATION = "Organization"
    REPOSITORY = "Repository"
    RESOURCE_SYNC = "ResourceSync"
    TEMPLATE_VERSION = "TemplateVersion"
    ENROLLMENT_CONFIG = "EnrollmentConfig"


LIST_ONLY_RESOURCES = frozenset({ResourceType.EVENT, ResourceType.ORGANIZATION})


NESTED_RESOURCES = frozenset({ResourceType.TEMPLATE_VERSION, ResourceType.CATALOG_ITEM})

API_MAPPING = {}


try:
    # v1beta1 Apis
    from flightctl.api.authprovider_api import AuthproviderApi
    from flightctl.api.device_api import DeviceApi
    from flightctl.api.event_api import EventApi
    from flightctl.api.fleet_api import FleetApi
    from flightctl.api.certificatesigningrequest_api import CertificatesigningrequestApi
    from flightctl.api.enrollmentrequest_api import EnrollmentrequestApi
    from flightctl.api.organization_api import OrganizationApi
    from flightctl.api.repository_api import RepositoryApi
    from flightctl.api.resourcesync_api import ResourcesyncApi

    # v1beta1 Models
    from flightctl.models.auth_provider import AuthProvider
    from flightctl.models.device import Device
    from flightctl.models.event import Event
    from flightctl.models.fleet import Fleet
    from flightctl.models.certificate_signing_request import CertificateSigningRequest
    from flightctl.models.enrollment_request import EnrollmentRequest
    from flightctl.models.organization import Organization
    from flightctl.models.repository import Repository
    from flightctl.models.resource_sync import ResourceSync
    from flightctl.models.enrollment_config import EnrollmentConfig
    from flightctl.models.template_version import TemplateVersion

    # v1alpha1 Apis
    from flightctl.v1alpha1.api.catalog_api import CatalogApi

    # v1alpha1 Models
    from flightctl.v1alpha1.models.catalog import Catalog
    from flightctl.v1alpha1.models.catalog_item import CatalogItem

    @dataclass
    class ApiResource:
        api: Union[
            AuthproviderApi, CatalogApi, DeviceApi, EventApi, FleetApi,
            CertificatesigningrequestApi, EnrollmentrequestApi,
            OrganizationApi, RepositoryApi, ResourcesyncApi,
        ]
        model: Union[
            AuthProvider, Catalog, CatalogItem, Device, Event, Fleet,
            CertificateSigningRequest, EnrollmentRequest, Organization,
            Repository, ResourceSync, EnrollmentConfig, TemplateVersion,
        ]

        api_version: str = "v1beta1"
        get: Optional[str] = None
        create: Optional[str] = None
        list: Optional[str] = None
        delete: Optional[str] = None
        patch: Optional[str] = None
        replace: Optional[str] = None
        rendered: Optional[str] = None
        decommission: Optional[str] = None

    API_MAPPING = {
        ResourceType.AUTH_PROVIDER: ApiResource(
            api=AuthproviderApi,
            model=AuthProvider,
            get='get_auth_provider',
            create='create_auth_provider',
            list='list_auth_providers',
            patch='patch_auth_provider',
            replace='replace_auth_provider',
            delete='delete_auth_provider',
        ),
        ResourceType.CATALOG: ApiResource(
            api=CatalogApi,
            model=Catalog,
            api_version='v1alpha1',
            get='get_catalog',
            create='create_catalog',
            list='list_catalogs',
            patch='patch_catalog',
            replace='replace_catalog',
            delete='delete_catalog',
        ),
        ResourceType.CATALOG_ITEM: ApiResource(
            api=CatalogApi,
            model=CatalogItem,
            api_version='v1alpha1',
            get='get_catalog_item',
            create='create_catalog_item',
            list='list_catalog_items',
            patch='patch_catalog_item',
            delete='delete_catalog_item',
        ),
        ResourceType.DEVICE: ApiResource(
            api=DeviceApi,
            model=Device,
            get='get_device',
            create='create_device',
            list='list_devices',
            patch='patch_device',
            replace='replace_device',
            delete='delete_device',
            rendered='get_rendered_device',
            decommission='decommission_device'

        ),
        ResourceType.FLEET: ApiResource(
            api=FleetApi,
            model=Fleet,
            get='get_fleet',
            create='create_fleet',
            list='list_fleets',
            patch='patch_fleet',
            replace='replace_fleet',
            delete='delete_fleet',
        ),
        ResourceType.CSR: ApiResource(
            api=CertificatesigningrequestApi,
            model=CertificateSigningRequest,
            get='get_certificate_signing_request',
            create='create_certificate_signing_request',
            list='list_certificate_signing_requests',
            patch='patch_certificate_signing_request',
            replace='replace_certificate_signing_request',
            delete='delete_certificate_signing_request',
        ),
        ResourceType.ENROLLMENT: ApiResource(
            api=EnrollmentrequestApi,
            model=EnrollmentRequest,
            get='get_enrollment_request',
            create='create_enrollment_request',
            list='list_enrollment_requests',
            replace='replace_enrollment_request',
            delete='delete_enrollment_request',
        ),
        ResourceType.REPOSITORY: ApiResource(
            api=RepositoryApi,
            model=Repository,
            get='get_repository',
            create='create_repository',
            list='list_repositories',
            patch='patch_repository',
            replace='replace_repository',
            delete='delete_repository',
        ),
        ResourceType.RESOURCE_SYNC: ApiResource(
            api=ResourcesyncApi,
            model=ResourceSync,
            get='get_resource_sync',
            create='create_resource_sync',
            list='list_resource_syncs',
            patch='patch_resource_sync',
            replace='replace_resource_sync',
            delete='delete_resource_sync',
        ),
        ResourceType.TEMPLATE_VERSION: ApiResource(
            api=FleetApi,
            model=TemplateVersion,
            get='get_template_version',
            list='list_template_versions',
            delete='delete_template_version',
        ),
        ResourceType.EVENT: ApiResource(
            api=EventApi,
            model=Event,
            list='list_events',
        ),
        ResourceType.ORGANIZATION: ApiResource(
            api=OrganizationApi,
            model=Organization,
            list='list_organizations',
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
