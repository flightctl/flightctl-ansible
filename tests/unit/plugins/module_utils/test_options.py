from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import ValidationException
from plugins.module_utils.options import GetOptions


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
