from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.template_version_list import TemplateVersionList
from ...types import UNSET, Response, Unset


def _get_kwargs(
    fleet: str,
    *,
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["continue"] = continue_

    params["labelSelector"] = label_selector

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/fleets/{fleet}/templateversions".format(
            fleet=fleet,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, TemplateVersionList]]:
    if response.status_code == 200:
        response_200 = TemplateVersionList.from_dict(response.json())

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
) -> Response[Union[Error, TemplateVersionList]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    fleet: str,
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Error, TemplateVersionList]]:
    """list template versions

    Args:
        fleet (str):
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, TemplateVersionList]]
    """

    kwargs = _get_kwargs(
        fleet=fleet,
        continue_=continue_,
        label_selector=label_selector,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    fleet: str,
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Error, TemplateVersionList]]:
    """list template versions

    Args:
        fleet (str):
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, TemplateVersionList]
    """

    return sync_detailed(
        fleet=fleet,
        client=client,
        continue_=continue_,
        label_selector=label_selector,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    fleet: str,
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Response[Union[Error, TemplateVersionList]]:
    """list template versions

    Args:
        fleet (str):
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, TemplateVersionList]]
    """

    kwargs = _get_kwargs(
        fleet=fleet,
        continue_=continue_,
        label_selector=label_selector,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    fleet: str,
    *,
    client: Union[AuthenticatedClient, Client],
    continue_: Union[Unset, str] = UNSET,
    label_selector: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
) -> Optional[Union[Error, TemplateVersionList]]:
    """list template versions

    Args:
        fleet (str):
        continue_ (Union[Unset, str]):
        label_selector (Union[Unset, str]):
        limit (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, TemplateVersionList]
    """

    return (
        await asyncio_detailed(
            fleet=fleet,
            client=client,
            continue_=continue_,
            label_selector=label_selector,
            limit=limit,
        )
    ).parsed
