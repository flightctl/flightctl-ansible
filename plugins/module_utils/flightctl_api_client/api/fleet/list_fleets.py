from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.fleet_list import FleetList
from ...models.sort_order import SortOrder
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    field_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    add_devices_count: Union[Unset, bool] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, SortOrder] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["continue"] = continue_

    params["labelSelector"] = label_selector

    params["fieldSelector"] = field_selector

    params["limit"] = limit

    params["owner"] = owner

    params["addDevicesCount"] = add_devices_count

    params["sortBy"] = sort_by

    json_sort_order: Union[Unset, str] = UNSET
    if not isinstance(sort_order, Unset):
        json_sort_order = sort_order

    params["sortOrder"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/fleets",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, FleetList]]:
    if response.status_code == 200:
        response_200 = FleetList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, FleetList]]:
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
    field_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    add_devices_count: Union[Unset, bool] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, SortOrder] = UNSET,
) -> Response[Union[Error, FleetList]]:
    """list Fleets

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        field_selector (Union[Unset, str]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        add_devices_count (Union[Unset, bool]):
        sort_by (Union[Unset, str]):
        sort_order (Union[Unset, SortOrder]): Specifies the sort order.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, FleetList]]
    """

    kwargs = _get_kwargs(
        continue_=continue_,
        label_selector=label_selector,
        field_selector=field_selector,
        limit=limit,
        owner=owner,
        add_devices_count=add_devices_count,
        sort_by=sort_by,
        sort_order=sort_order,
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
    field_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    add_devices_count: Union[Unset, bool] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, SortOrder] = UNSET,
) -> Optional[Union[Error, FleetList]]:
    """list Fleets

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        field_selector (Union[Unset, str]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        add_devices_count (Union[Unset, bool]):
        sort_by (Union[Unset, str]):
        sort_order (Union[Unset, SortOrder]): Specifies the sort order.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, FleetList]
    """

    return sync_detailed(
        client=client,
        continue_=continue_,
        label_selector=label_selector,
        field_selector=field_selector,
        limit=limit,
        owner=owner,
        add_devices_count=add_devices_count,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    field_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    add_devices_count: Union[Unset, bool] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, SortOrder] = UNSET,
) -> Response[Union[Error, FleetList]]:
    """list Fleets

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        field_selector (Union[Unset, str]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        add_devices_count (Union[Unset, bool]):
        sort_by (Union[Unset, str]):
        sort_order (Union[Unset, SortOrder]): Specifies the sort order.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, FleetList]]
    """

    kwargs = _get_kwargs(
        continue_=continue_,
        label_selector=label_selector,
        field_selector=field_selector,
        limit=limit,
        owner=owner,
        add_devices_count=add_devices_count,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    field_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    owner: Union[Unset, str] = UNSET,
    add_devices_count: Union[Unset, bool] = UNSET,
    sort_by: Union[Unset, str] = UNSET,
    sort_order: Union[Unset, SortOrder] = UNSET,
) -> Optional[Union[Error, FleetList]]:
    """list Fleets

    Args:
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        field_selector (Union[Unset, str]):
        limit (Union[Unset, int]):
        owner (Union[Unset, str]):
        add_devices_count (Union[Unset, bool]):
        sort_by (Union[Unset, str]):
        sort_order (Union[Unset, SortOrder]): Specifies the sort order.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, FleetList]
    """

    return (
        await asyncio_detailed(
            client=client,
            continue_=continue_,
            label_selector=label_selector,
            field_selector=field_selector,
            limit=limit,
            owner=owner,
            add_devices_count=add_devices_count,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
