from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

import pytest

from plugins.module_utils.sdk_utils import (
    is_pydantic_validation_error,
    normalize_sdk_output,
    raw_response_to_dict,
)


def _make_pydantic_error(msg="boom"):
    """Build an exception that matches the pydantic ValidationError heuristic.

    Detection is by type name + module so we do not need pydantic installed.
    """
    class ValidationError(Exception):
        __module__ = "pydantic_core._pydantic_core"

    return ValidationError(msg)


class TestIsPydanticValidationError:
    def test_detects_stand_in_pydantic_error(self):
        assert is_pydantic_validation_error(_make_pydantic_error()) is True

    def test_detects_real_pydantic_error(self):
        try:
            from pydantic import BaseModel, ValidationError  # noqa: F401
        except ImportError:
            pytest.skip("pydantic not installed")

        class StrictModel(BaseModel):
            value: int

        try:
            StrictModel(value="not-an-int")  # type: ignore[arg-type]
        except ValidationError as exc:
            assert is_pydantic_validation_error(exc) is True

    def test_generic_exception_returns_false(self):
        assert is_pydantic_validation_error(ValueError("nope")) is False

    def test_non_pydantic_validation_error_returns_false(self):
        class ValidationError(Exception):
            __module__ = "myapp.errors"

        assert is_pydantic_validation_error(ValidationError("nope")) is False


class TestRawResponseToDict:
    def test_parses_json_body(self):
        response = type("Resp", (), {})()
        response.data = json.dumps({"items": [1, 2, 3]}).encode()
        assert raw_response_to_dict(response) == {"items": [1, 2, 3]}


class TestNormalizeSdkOutput:
    def test_masks_nested_pydantic_secret_strings(self):
        class SecretStr:
            __module__ = "pydantic.types"

            def __str__(self):
                return "**********"

            def get_secret_value(self):
                return "real-token"

        normalized = normalize_sdk_output({
            "spec": {
                "actions": [
                    {"auth": {"bearerToken": SecretStr()}},
                ]
            }
        })

        assert normalized["spec"]["actions"][0]["auth"]["bearerToken"] == "**********"
        assert "real-token" not in json.dumps(normalized)

    def test_preserves_json_compatible_values(self):
        value = {"items": ["value", 1, True, None]}

        assert normalize_sdk_output(value) == value
