# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Any, Dict, Iterable, List, Optional, Union, cast

from .constants import API_MAPPING, ResourceType

try:
    import yaml
except ImportError as imp_exc:
    PYYAML_IMPORT_ERROR = imp_exc
else:
    PYYAML_IMPORT_ERROR = None

_DEFAULT_API_VERSION = "flightctl.io/v1beta1"


def _api_version_for_kind(kind: Optional[str]) -> str:
    """Return the correct apiVersion string for a given resource kind."""
    if kind:
        normalized = kind[:-4] if kind.endswith("List") else kind
        try:
            resource = ResourceType(normalized)
            mapping = API_MAPPING.get(resource)
            if mapping and mapping.api_version == "v1alpha1":
                return "flightctl.io/v1alpha1"
        except (TypeError, ValueError):
            pass
    return _DEFAULT_API_VERSION


class ResourceDefinition(Dict[str, Any]):
    """
    Representation of a resource definition.
    """

    @property
    def kind(self) -> Optional[str]:
        return self.get("kind")

    @property
    def api_version(self) -> Optional[str]:
        return self.get("apiVersion")

    @property
    def name(self) -> Optional[str]:
        metadata = self.get("metadata", {})
        return metadata.get("name")


def from_yaml(definition: Union[str, List, Dict]) -> Iterable[Dict]:
    """Load resource definitions from a yaml definition."""
    if PYYAML_IMPORT_ERROR:
        raise PYYAML_IMPORT_ERROR

    definitions: List[Dict] = []
    if isinstance(definition, str):
        definitions += yaml.safe_load_all(definition)
    elif isinstance(definition, list):
        for item in definition:
            if isinstance(item, str):
                definitions += yaml.safe_load_all(item)
            else:
                definitions.append(item)
    else:
        definition = cast(Dict, definition)
        definitions.append(definition)

    return filter(None, definitions)


def merge_params(definition: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Merge module parameters with the resource definition.

    Fields in the resource definition take precedence over module parameters.
    """
    definition.setdefault("kind", params.get("kind"))
    api_version = params.get("api_version") or _api_version_for_kind(definition.get("kind"))
    definition.setdefault("apiVersion", api_version)
    metadata = definition.setdefault("metadata", {})
    if params.get("name"):
        metadata.setdefault("name", params.get("name"))
    if params.get("catalog_name"):
        metadata.setdefault("catalog", params.get("catalog_name"))
    return definition


def flatten_list_kind(definition: Dict[str, Any], params: Dict[str, Any]) -> List[Dict]:
    """Replace *List kind with the items it contains.

    This will take a definition for a *List resource and return a list of
    definitions for the items contained within the List.
    """
    items = []
    kind = cast(str, definition.get("kind"))[:-4]
    api_version = definition.get("apiVersion")
    for item in definition.get("items", []):
        item.setdefault("kind", kind)
        item.setdefault("apiVersion", api_version)
        items.append(merge_params(item, params))
    return items


def create_definitions(params: Dict) -> List[ResourceDefinition]:
    """Create a list of ResourceDefinitions from module inputs.

    This will take the module's inputs and return a list of ResourceDefintion
    objects. The resource definitions returned by this function should be as
    complete a definition as we can create based on the input. Any *List kinds
    will be removed and replaced by the resources contained in it.
    """
    if params.get("resource_definition"):
        d = cast(Union[str, List, Dict], params.get("resource_definition"))
        definitions = from_yaml(d)
    else:
        # We'll create an empty definition and let merge_params set values
        # from the module parameters.
        definitions = [{}]

    resource_definitions: List[Dict] = []
    for definition in definitions:
        merge_params(definition, params)
        kind = cast(Optional[str], definition.get("kind"))
        if kind and kind.endswith("List"):
            resource_definitions += flatten_list_kind(definition, params)
        else:
            resource_definitions.append(definition)
    return list(map(ResourceDefinition, resource_definitions))
