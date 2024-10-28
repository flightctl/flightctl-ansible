from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.rendered_device_spec import RenderedDeviceSpec
from ...types import UNSET, Response, Unset


def _get_kwargs(
    name: str,
    *,
    known_rendered_version: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["knownRenderedVersion"] = known_rendered_version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/devices/{name}/rendered".format(
            name=name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, Error, RenderedDeviceSpec]]:
    if response.status_code == 200:
        response_200 = RenderedDeviceSpec.from_dict(response.json())

        return response_200
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404
    if response.status_code == 409:
        response_409 = Error.from_dict(response.json())

        return response_409
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, Error, RenderedDeviceSpec]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    known_rendered_version: Union[Unset, str] = UNSET,
) -> Response[Union[Any, Error, RenderedDeviceSpec]]:
    """get the full specification for the specified device

    Args:
        name (str):
        known_rendered_version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, RenderedDeviceSpec]]
    """

    kwargs = _get_kwargs(
        name=name,
        known_rendered_version=known_rendered_version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    known_rendered_version: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, Error, RenderedDeviceSpec]]:
    """get the full specification for the specified device

    Args:
        name (str):
        known_rendered_version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, RenderedDeviceSpec]
    """

    return sync_detailed(
        name=name,
        client=client,
        known_rendered_version=known_rendered_version,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    known_rendered_version: Union[Unset, str] = UNSET,
) -> Response[Union[Any, Error, RenderedDeviceSpec]]:
    """get the full specification for the specified device

    Args:
        name (str):
        known_rendered_version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, Error, RenderedDeviceSpec]]
    """

    kwargs = _get_kwargs(
        name=name,
        known_rendered_version=known_rendered_version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    known_rendered_version: Union[Unset, str] = UNSET,
) -> Optional[Union[Any, Error, RenderedDeviceSpec]]:
    """get the full specification for the specified device

    Args:
        name (str):
        known_rendered_version (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, Error, RenderedDeviceSpec]
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            known_rendered_version=known_rendered_version,
        )
    ).parsed
