from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.template_version import TemplateVersion
from ...types import Response


def _get_kwargs(
    fleet: str,
    name: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/fleets/{fleet}/templateversions/{name}".format(
            fleet=fleet,
            name=name,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, TemplateVersion]]:
    if response.status_code == 200:
        response_200 = TemplateVersion.from_dict(response.json())

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
) -> Response[Union[Error, TemplateVersion]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    fleet: str,
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Error, TemplateVersion]]:
    """read the specified template version

    Args:
        fleet (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, TemplateVersion]]
    """

    kwargs = _get_kwargs(
        fleet=fleet,
        name=name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    fleet: str,
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Error, TemplateVersion]]:
    """read the specified template version

    Args:
        fleet (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, TemplateVersion]
    """

    return sync_detailed(
        fleet=fleet,
        name=name,
        client=client,
    ).parsed


async def asyncio_detailed(
    fleet: str,
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Error, TemplateVersion]]:
    """read the specified template version

    Args:
        fleet (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, TemplateVersion]]
    """

    kwargs = _get_kwargs(
        fleet=fleet,
        name=name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    fleet: str,
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Error, TemplateVersion]]:
    """read the specified template version

    Args:
        fleet (str):
        name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, TemplateVersion]
    """

    return (
        await asyncio_detailed(
            fleet=fleet,
            name=name,
            client=client,
        )
    ).parsed
