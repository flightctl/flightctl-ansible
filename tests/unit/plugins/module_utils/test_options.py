from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import ValidationException
from plugins.module_utils.options import ApplicationOptions, GetOptions


class TestGetOptionsListOnlyResources:
    """Validate that list-only resources (Event, Organization) reject get-by-name."""

    def test_event_with_name_raises(self):
        with pytest.raises(ValidationException, match="Event only supports listing"):
            GetOptions(resource=ResourceType.EVENT, name="some-event")

    def test_organization_with_name_raises(self):
        with pytest.raises(ValidationException, match="Organization only supports listing"):
            GetOptions(resource=ResourceType.ORGANIZATION, name="some-org")

    def test_event_without_name_succeeds(self):
        opts = GetOptions(resource=ResourceType.EVENT)
        assert opts.resource is ResourceType.EVENT
        assert opts.name is None

    def test_organization_without_name_succeeds(self):
        opts = GetOptions(resource=ResourceType.ORGANIZATION)
        assert opts.resource is ResourceType.ORGANIZATION
        assert opts.name is None

    def test_event_with_field_selector(self):
        opts = GetOptions(resource=ResourceType.EVENT, field_selector="source.kind=Device")
        assert opts.field_selector == "source.kind=Device"

    def test_organization_with_field_selector(self):
        opts = GetOptions(resource=ResourceType.ORGANIZATION, field_selector="metadata.name=myorg")
        assert opts.field_selector == "metadata.name=myorg"

    def test_event_with_limit(self):
        opts = GetOptions(resource=ResourceType.EVENT, limit=10)
        assert opts.request_params['limit'] == 10


class TestGetOptionsAuthProvider:
    """Validate that AuthProvider supports standard get-by-name operations."""

    def test_auth_provider_with_name_succeeds(self):
        opts = GetOptions(resource=ResourceType.AUTH_PROVIDER, name="my-provider")
        assert opts.resource is ResourceType.AUTH_PROVIDER
        assert opts.name == "my-provider"

    def test_auth_provider_without_name_succeeds(self):
        opts = GetOptions(resource=ResourceType.AUTH_PROVIDER)
        assert opts.resource is ResourceType.AUTH_PROVIDER
        assert opts.name is None


class TestGetOptionsCatalog:
    """Validate Catalog (non-nested) and CatalogItem (nested) options."""

    def test_catalog_with_name_succeeds(self):
        opts = GetOptions(resource=ResourceType.CATALOG, name="my-catalog")
        assert opts.resource is ResourceType.CATALOG
        assert opts.name == "my-catalog"
        assert opts.parent_name is None

    def test_catalog_without_name_succeeds(self):
        opts = GetOptions(resource=ResourceType.CATALOG)
        assert opts.resource is ResourceType.CATALOG

    def test_catalog_item_with_catalog_name(self):
        opts = GetOptions(resource=ResourceType.CATALOG_ITEM, name="my-item", catalog_name="my-catalog")
        assert opts.parent_name == "my-catalog"
        assert opts.deployments is False

    def test_catalog_item_deployments_with_catalog_name_and_item_name(self):
        opts = GetOptions(
            resource=ResourceType.CATALOG_ITEM,
            name="my-item",
            catalog_name="my-catalog",
            deployments=True,
        )
        assert opts.deployments is True

    def test_deployments_invalid_for_non_catalog_item(self):
        with pytest.raises(ValidationException, match="Deployments field is only valid for CatalogItem kind"):
            GetOptions(resource=ResourceType.DEVICE, name="device-1", deployments=True)

    def test_catalog_item_deployments_without_item_name_raises(self):
        with pytest.raises(ValidationException, match="Deployments field requires catalog name and item name"):
            GetOptions(
                resource=ResourceType.CATALOG_ITEM,
                catalog_name="my-catalog",
                deployments=True,
            )

    def test_catalog_item_deployments_without_catalog_name_raises(self):
        with pytest.raises(ValidationException, match="Deployments field requires catalog name and item name"):
            GetOptions(
                resource=ResourceType.CATALOG_ITEM,
                name="my-item",
                deployments=True,
            )

    def test_catalog_item_without_catalog_name_raises(self):
        with pytest.raises(ValidationException, match="CatalogItem requires a parent name"):
            GetOptions(resource=ResourceType.CATALOG_ITEM, name="my-item")

    def test_catalog_item_list_with_catalog_name(self):
        opts = GetOptions(resource=ResourceType.CATALOG_ITEM, catalog_name="my-catalog")
        assert opts.parent_name == "my-catalog"
        assert opts.name is None

    def test_catalog_name_invalid_for_non_catalog_item(self):
        with pytest.raises(ValidationException, match="Catalog name field is only valid for CatalogItem"):
            GetOptions(resource=ResourceType.DEVICE, catalog_name="my-catalog")

    def test_template_version_parent_name_via_fleet_name(self):
        opts = GetOptions(resource=ResourceType.TEMPLATE_VERSION, fleet_name="my-fleet")
        assert opts.parent_name == "my-fleet"

    def test_template_version_without_fleet_name_raises(self):
        with pytest.raises(ValidationException, match="TemplateVersion requires a parent name"):
            GetOptions(resource=ResourceType.TEMPLATE_VERSION)


class TestApplicationOptions:
    def test_device_action_options_are_valid(self):
        options = ApplicationOptions(
            resource=ResourceType.DEVICE,
            name="edge-1",
            app_name="workload",
            state="started",
        )

        assert options.resource is ResourceType.DEVICE
        assert options.name == "edge-1"
        assert options.app_name == "workload"
        assert options.state == "started"

    def test_rejects_unsupported_resource(self):
        with pytest.raises(
            ValidationException,
            match="CertificateSigningRequest does not support application actions",
        ):
            ApplicationOptions(ResourceType.CSR, "request-1", "workload", "started")

    def test_rejects_missing_target_name(self):
        with pytest.raises(ValidationException, match="Name must be specified"):
            ApplicationOptions(ResourceType.DEVICE, "", "workload", "started")

    def test_rejects_missing_application_name(self):
        with pytest.raises(ValidationException, match="Application name must be specified"):
            ApplicationOptions(ResourceType.DEVICE, "edge-1", "", "started")

    def test_rejects_invalid_state(self):
        with pytest.raises(ValidationException, match="Invalid application state: running"):
            ApplicationOptions(ResourceType.DEVICE, "edge-1", "workload", "running")

    def test_rejects_fleet_restart(self):
        with pytest.raises(
            ValidationException,
            match="Restarting applications is only supported for Device",
        ):
            ApplicationOptions(ResourceType.FLEET, "fleet-a", "workload", "restarted")
