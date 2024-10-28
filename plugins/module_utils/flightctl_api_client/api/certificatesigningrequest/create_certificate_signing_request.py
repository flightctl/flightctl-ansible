from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.certificate_signing_request import CertificateSigningRequest
from ...models.enrollment_request import EnrollmentRequest
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    *,
    body: CertificateSigningRequest,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/certificatesigningrequests",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CertificateSigningRequest, EnrollmentRequest, Error]]:
    if response.status_code == 200:
        response_200 = CertificateSigningRequest.from_dict(response.json())

        return response_200
    if response.status_code == 201:
        response_201 = CertificateSigningRequest.from_dict(response.json())

        return response_201
    if response.status_code == 202:
        response_202 = CertificateSigningRequest.from_dict(response.json())

        return response_202
    if response.status_code == 208:
        response_208 = EnrollmentRequest.from_dict(response.json())

        return response_208
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
) -> Response[Union[CertificateSigningRequest, EnrollmentRequest, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CertificateSigningRequest,
) -> Response[Union[CertificateSigningRequest, EnrollmentRequest, Error]]:
    """request Certificate Signing

    Args:
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CertificateSigningRequest, EnrollmentRequest, Error]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CertificateSigningRequest,
) -> Optional[Union[CertificateSigningRequest, EnrollmentRequest, Error]]:
    """request Certificate Signing

    Args:
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CertificateSigningRequest, EnrollmentRequest, Error]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CertificateSigningRequest,
) -> Response[Union[CertificateSigningRequest, EnrollmentRequest, Error]]:
    """request Certificate Signing

    Args:
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CertificateSigningRequest, EnrollmentRequest, Error]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CertificateSigningRequest,
) -> Optional[Union[CertificateSigningRequest, EnrollmentRequest, Error]]:
    """request Certificate Signing

    Args:
        body (CertificateSigningRequest): CertificateSigningRequest represents a request for a
            signed certificate from the CA

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CertificateSigningRequest, EnrollmentRequest, Error]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
