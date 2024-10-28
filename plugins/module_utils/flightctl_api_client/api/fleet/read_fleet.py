from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.fleet import Fleet
from ...types import UNSET, Response, Unset


def _get_kwargs(
    name: str,
    *,
    add_devices_summary: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["addDevicesSummary"] = add_devices_summary

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/fleets/{name}".format(
            name=name,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, Fleet]]:
    if response.status_code == 200:
        response_200 = Fleet.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, Fleet]]:
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
    add_devices_summary: Union[Unset, bool] = UNSET,
) -> Response[Union[Error, Fleet]]:
    """read the specified Fleet

    Args:
        name (str):
        add_devices_summary (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Fleet]]
    """

    kwargs = _get_kwargs(
        name=name,
        add_devices_summary=add_devices_summary,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    add_devices_summary: Union[Unset, bool] = UNSET,
) -> Optional[Union[Error, Fleet]]:
    """read the specified Fleet

    Args:
        name (str):
        add_devices_summary (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Fleet]
    """

    return sync_detailed(
        name=name,
        client=client,
        add_devices_summary=add_devices_summary,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    add_devices_summary: Union[Unset, bool] = UNSET,
) -> Response[Union[Error, Fleet]]:
    """read the specified Fleet

    Args:
        name (str):
        add_devices_summary (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Fleet]]
    """

    kwargs = _get_kwargs(
        name=name,
        add_devices_summary=add_devices_summary,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    add_devices_summary: Union[Unset, bool] = UNSET,
) -> Optional[Union[Error, Fleet]]:
    """read the specified Fleet

    Args:
        name (str):
        add_devices_summary (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Fleet]
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            add_devices_summary=add_devices_summary,
        )
    ).parsed
