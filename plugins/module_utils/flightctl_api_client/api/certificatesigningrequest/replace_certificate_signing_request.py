from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.certificate_signing_request import CertificateSigningRequest
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    name: str,
    *,
    body: CertificateSigningRequest,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/certificatesigningrequests/{name}".format(
            name=name,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CertificateSigningRequest, Error]]:
    if response.status_code == 200:
        response_200 = CertificateSigningRequest.from_dict(response.json())

        return response_200
    if response.status_code == 201:
        response_201 = CertificateSigningRequest.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400
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
) -> Response[Union[CertificateSigningRequest, Error]]:
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
    body: CertificateSigningRequest,
) -> Response[Union[CertificateSigningRequest, Error]]:
    """replace the specified CertificateSigningRequest

    Args:
        name (str):
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CertificateSigningRequest, Error]]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: CertificateSigningRequest,
) -> Optional[Union[CertificateSigningRequest, Error]]:
    """replace the specified CertificateSigningRequest

    Args:
        name (str):
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CertificateSigningRequest, Error]
    """

    return sync_detailed(
        name=name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: CertificateSigningRequest,
) -> Response[Union[CertificateSigningRequest, Error]]:
    """replace the specified CertificateSigningRequest

    Args:
        name (str):
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CertificateSigningRequest, Error]]
    """

    kwargs = _get_kwargs(
        name=name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: CertificateSigningRequest,
) -> Optional[Union[CertificateSigningRequest, Error]]:
    """replace the specified CertificateSigningRequest

    Args:
        name (str):
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CertificateSigningRequest, Error]
    """

    return (
        await asyncio_detailed(
            name=name,
            client=client,
            body=body,
        )
    ).parsed
