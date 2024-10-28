from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_list import DeviceList
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    status_filter: Union[Unset, List[str]] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    summary_only: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["continue"] = continue_

    params["labelSelector"] = label_selector

    json_status_filter: Union[Unset, List[str]] = UNSET
    if not isinstance(status_filter, Unset):
        json_status_filter = status_filter

    params["statusFilter"] = json_status_filter

    params["limit"] = limit

    params["owner"] = owner

    params["summaryOnly"] = summary_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/devices",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DeviceList, Error]]:
    if response.status_code == 200:
        response_200 = DeviceList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[DeviceList, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    status_filter: Union[Unset, List[str]] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    summary_only: Union[Unset, bool] = UNSET,
) -> Response[Union[DeviceList, Error]]:
    """list Devices

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        status_filter (Union[Unset, List[str]]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        summary_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceList, Error]]
    """

    kwargs = _get_kwargs(
        continue_=continue_,
        label_selector=label_selector,
        status_filter=status_filter,
        limit=limit,
        owner=owner,
        summary_only=summary_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    status_filter: Union[Unset, List[str]] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    summary_only: Union[Unset, bool] = UNSET,
) -> Optional[Union[DeviceList, Error]]:
    """list Devices

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        status_filter (Union[Unset, List[str]]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        summary_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceList, Error]
    """

    return sync_detailed(
        client=client,
        continue_=continue_,
        label_selector=label_selector,
        status_filter=status_filter,
        limit=limit,
        owner=owner,
        summary_only=summary_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    status_filter: Union[Unset, List[str]] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    summary_only: Union[Unset, bool] = UNSET,
) -> Response[Union[DeviceList, Error]]:
    """list Devices

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        status_filter (Union[Unset, List[str]]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        summary_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceList, Error]]
    """

    kwargs = _get_kwargs(
        continue_=continue_,
        label_selector=label_selector,
        status_filter=status_filter,
        limit=limit,
        owner=owner,
        summary_only=summary_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    status_filter: Union[Unset, List[str]] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    summary_only: Union[Unset, bool] = UNSET,
) -> Optional[Union[DeviceList, Error]]:
    """list Devices

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        status_filter (Union[Unset, List[str]]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        summary_only (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceList, Error]
    """

    return (
        await asyncio_detailed(
            client=client,
            continue_=continue_,
            label_selector=label_selector,
            status_filter=status_filter,
            limit=limit,
            owner=owner,
            summary_only=summary_only,
        )
    ).parsed
