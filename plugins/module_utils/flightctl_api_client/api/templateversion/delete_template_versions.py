from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.status import Status
from ...types import Response


def _get_kwargs(
    fleet: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/fleets/{fleet}/templateversions".format(
            fleet=fleet,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Error, Status]]:
    if response.status_code == 200:
        response_200 = Status.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Error, Status]]:
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
) -> Response[Union[Error, Status]]:
    """delete a collection of template versions

    Args:
        fleet (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Status]]
    """

    kwargs = _get_kwargs(
        fleet=fleet,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    fleet: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Error, Status]]:
    """delete a collection of template versions

    Args:
        fleet (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Status]
    """

    return sync_detailed(
        fleet=fleet,
        client=client,
    ).parsed


async def asyncio_detailed(
    fleet: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Error, Status]]:
    """delete a collection of template versions

    Args:
        fleet (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Status]]
    """

    kwargs = _get_kwargs(
        fleet=fleet,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    fleet: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Error, Status]]:
    """delete a collection of template versions

    Args:
        fleet (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Status]
    """

    return (
        await asyncio_detailed(
            fleet=fleet,
            client=client,
        )
    ).parsed
