# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from typing import Any, Dict

_MASKED_VALUE_PLACEHOLDER = "*****"


def is_pydantic_validation_error(exc: Exception) -> bool:
    """Check if an exception is a pydantic ValidationError without importing pydantic.

    The Flight Control client SDK deserializes API responses into pydantic
    models. When a response contains data that violates a model's schema (for
    example, a mount-only ``ApplicationVolume`` that lacks the required ``image``
    field), pydantic raises a ``ValidationError`` that is *not* a subclass of the
    SDK's ``ApiException``. Detecting it by type name avoids importing pydantic
    directly, which is only a transitive dependency of the client SDK.
    """
    exc_type = type(exc)
    return exc_type.__name__ == "ValidationError" and "pydantic" in getattr(
        exc_type, "__module__", ""
    )


def normalize_sdk_output(value: Any) -> Any:
    """Convert SDK values into JSON-safe output without exposing secrets.

    Pydantic ``SecretStr`` values returned by the generated client cannot be
    serialized by Ansible's JSON encoder. Replace them with Flight Control's
    masked-value placeholder so the output can be safely reused in update and
    replace requests without changing the stored secret.
    """
    value_type = type(value)
    if value_type.__name__ == "SecretStr" and "pydantic" in getattr(
        value_type, "__module__", ""
    ):
        return _MASKED_VALUE_PLACEHOLDER
    if isinstance(value, dict):
        return {key: normalize_sdk_output(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_sdk_output(item) for item in value]
    if isinstance(value, tuple):
        return tuple(normalize_sdk_output(item) for item in value)
    return value


# pylint: disable=too-many-return-statements
def serialize_sdk_output(value: Any) -> Any:
    """Serialize a generated SDK response without dropping read-only fields.

    Generated client ``to_dict()`` methods are also used for request payloads
    and therefore omit OpenAPI read-only properties.  Info modules need the
    complete response representation, including rendered delta hints.  Use
    pydantic's response-oriented dump here, while keeping request serialization
    unchanged.  ``additional_properties`` is an internal SDK bookkeeping field
    and is intentionally not exposed in Ansible output.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        if value.get("actual_instance") is not None:
            return serialize_sdk_output(value["actual_instance"])
        return normalize_sdk_output(
            {
                key: serialize_sdk_output(item)
                for key, item in value.items()
                if key != "additional_properties"
            }
        )
    if isinstance(value, (list, tuple)):
        return [serialize_sdk_output(item) for item in value]

    model_fields = getattr(type(value), "model_fields", None)
    model_dump = getattr(type(value), "model_dump", None)
    if isinstance(model_fields, dict) and callable(model_dump):
        if "actual_instance" in model_fields:
            actual_instance = getattr(value, "actual_instance", None)
            if actual_instance is not None:
                return serialize_sdk_output(actual_instance)
        try:
            dumped = value.model_dump(by_alias=True, exclude_none=True)
        except (TypeError, ValueError):
            dumped = value.to_dict()
        return serialize_sdk_output(dumped)

    to_dict = getattr(type(value), "to_dict", None)
    if callable(to_dict):
        return serialize_sdk_output(value.to_dict())

    # Unit tests and callers may provide lightweight response doubles whose
    # ``to_dict`` method exists only on the instance. Avoid recursing through
    # an unconfigured MagicMock while retaining the established behavior for
    # configured doubles.
    if type(value).__module__ == "unittest.mock" and hasattr(value, "to_dict"):
        converted = value.to_dict()
        if converted is not value and type(converted).__module__ != "unittest.mock":
            return serialize_sdk_output(converted)

    return normalize_sdk_output(value)


def raw_response_to_dict(response: Any) -> Dict[str, Any]:
    """Deserialize the body of a ``*_without_preload_content`` response to a dict.

    The SDK's ``*_without_preload_content`` endpoints return the raw HTTP
    response without pydantic model construction; the JSON payload is available
    on ``response.data``. This is used as a fallback when normal deserialization
    fails with a pydantic ``ValidationError``.
    """
    return json.loads(response.data)
