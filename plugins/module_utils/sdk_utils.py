# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
from typing import Any, Dict


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
    return exc_type.__name__ == 'ValidationError' and 'pydantic' in getattr(exc_type, '__module__', '')


def normalize_sdk_output(value: Any) -> Any:
    """Convert SDK values into JSON-safe output without exposing secrets.

    Pydantic ``SecretStr`` values returned by the generated client cannot be
    serialized by Ansible's JSON encoder. Converting them with ``str()`` keeps
    Pydantic's masked representation while recursively preserving the rest of
    the response structure.
    """
    value_type = type(value)
    if value_type.__name__ == 'SecretStr' and 'pydantic' in getattr(value_type, '__module__', ''):
        return str(value)
    if isinstance(value, dict):
        return {key: normalize_sdk_output(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_sdk_output(item) for item in value]
    if isinstance(value, tuple):
        return tuple(normalize_sdk_output(item) for item in value)
    return value


def raw_response_to_dict(response: Any) -> Dict[str, Any]:
    """Deserialize the body of a ``*_without_preload_content`` response to a dict.

    The SDK's ``*_without_preload_content`` endpoints return the raw HTTP
    response without pydantic model construction; the JSON payload is available
    on ``response.data``. This is used as a fallback when normal deserialization
    fails with a pydantic ``ValidationError``.
    """
    return json.loads(response.data)
